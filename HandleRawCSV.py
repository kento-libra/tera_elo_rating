import pandas as pd
import numpy as np
import japanize_matplotlib
import pickle
from tqdm import tqdm
import matplotlib.pyplot as plt
import elo_calc
import funcs

class HandleRawCSV:
    def __init__(self,
                kEnqueteCsvPathPaperEnqueteData,
                kEnqueteCsvPathDigitalEnqueteData, 
                kEnqueteCsvPathTitleData,
                kEnqueteTitleMinimumIssue = 10,
                kEnqueteTargetYear = 2021,
                isWeightedByReadSegment=False,
                NumRandomLosers=0,
                division='All'
                ):
        self.isWeightedByReadSegment=isWeightedByReadSegment
        self.NumRandomLosers=NumRandomLosers
        self.division=division
        enquete_data = pd.read_csv(kEnqueteCsvPathPaperEnqueteData)
        enquete_data_digital = pd.read_csv(kEnqueteCsvPathDigitalEnqueteData)
        title_data = pd.read_csv(kEnqueteCsvPathTitleData)
        title_data_only = title_data[['title_code', 'title']]

        enquete_data_merged = pd.merge(enquete_data, title_data_only, left_on='title_1', right_on='title_code', suffixes=['', '_1'])\
                                .drop(columns=['title_code', 'title_1'])\
                                .rename(columns={'title': 'title_1'})
        enquete_data_merged = pd.merge(enquete_data_merged, title_data_only, left_on='title_2', right_on='title_code', suffixes=['', '_2'])\
                                .drop(columns=['title_code', 'title_2'])\
                                .rename(columns={'title': 'title_2'})
        enquete_data_merged = pd.merge(enquete_data_merged, title_data_only, left_on='title_3', right_on='title_code', suffixes=['', '_3'])\
                                .drop(columns=['title_code', 'title_3'])\
                                .rename(columns={'title': 'title_3'})
        # 読み切りなどを削除 'year == @kEnqueteTargetYear'
        if division is not 'All':
            enquete_data_digital=enquete_data_digital.query(division)
            enquete_data_merged=enquete_data_merged.query(division)
        self.enquete_data_digital_filtered = enquete_data_digital.query('not age.str.contains("\|")')\
                                                    .groupby('title_1')\
                                                    .filter(lambda x: x['issue'].groupby(x['title_1']).nunique().max() >= kEnqueteTitleMinimumIssue)
        self.enquete_data_digital_filtered.loc[:,'read_segment'] = self.enquete_data_digital_filtered.loc[:,'read_segment'].replace('全部読んでいる', '25')
        self.enquete_data_digital_filtered.loc[:,'read_segment'] = self.enquete_data_digital_filtered.loc[:,'age'].replace('(\d+).*', r'\1',regex=True)
        self.enquete_data_digital_filtered.loc[:,'age'] = self.enquete_data_digital_filtered.loc[:,'age'].replace('(\d+).*', r'\1',regex=True)
        self.enquete_data_filtered = enquete_data_merged\
                                        .groupby('title_1')\
                                        .filter(lambda x: x['issue'].groupby(x['title_1']).nunique().max() >= kEnqueteTitleMinimumIssue)
        players_1 = self.enquete_data_filtered.groupby('title_1').groups.keys()
        players_2 = self.enquete_data_filtered.groupby('title_2').groups.keys()
        players_3 = self.enquete_data_filtered.groupby('title_3').groups.keys()
        players_d1 = self.enquete_data_digital_filtered.groupby('title_1').groups.keys()
        players_d2 = self.enquete_data_digital_filtered.groupby('title_2').groups.keys()
        players_d3 = self.enquete_data_digital_filtered.groupby('title_3').groups.keys()

        all_players = players_1 | players_2 | players_3 | players_d1 | players_d2 | players_d3

        players = pd.DataFrame(all_players, columns=['name'])
        players = players.set_index('name')
        self.enquete_data_digital_filtered['issue']=(self.enquete_data_digital_filtered['year'].astype(str)+self.enquete_data_digital_filtered['issue'].astype(str).str.zfill(2)).astype(int)
        self.enquete_data_filtered['issue']=(self.enquete_data_filtered['year'].astype(str)+self.enquete_data_filtered['issue'].astype(str).str.zfill(2)).astype(int)
        self.enquete_data_filtered['read_segment']=1
        #issue_list=enquete_data_digital_filtered.loc[:,'issue'].unique()
        # unique_list=[]
        # for i in issue_list:
        #     issue_clip=enquete_data_digital_filtered.query('issue == {}'.format(i)).loc[:,'title_1':'title_3']
        #     tmp=issue_clip['title_1']
        #     tmp=pd.concat([tmp,issue_clip['title_2']])
        #     tmp=pd.concat([tmp,issue_clip['title_3']])
        #     issue_unique_list=tmp.unique()
        #     unique_list.append([issue_unique_list,i])
        # unique_list=pd.DataFrame(unique_list, columns=['list','issue'])
        issue_num_digital = self.enquete_data_digital_filtered['issue']
        issue_num_paper = self.enquete_data_filtered['issue']
        self.issue_num_list = np.intersect1d(issue_num_digital.unique(), issue_num_paper.unique())
        self.issue_num_list.sort()
        print('Initing Done!')
    
    def fit(self):
        results_digital=funcs.TranslateResult(self.enquete_data_digital_filtered,self.isWeightedByReadSegment,self.NumRandomLosers)
        #results_paper=funcs.TranslateResult(self.enquete_data_filtered,self.isWeightedByReadSegment,self.NumRandomLosers)
        print('Translating Done!')
        print(results_digital)
        self.elo_rating_digital = funcs.CalcElo(results_digital, self.issue_num_list)
        #self.elo_rating_paper = funcs.CalcElo(results_paper, self.issue_num_list)
        print('Fitting Done!')
    def savepickle(self,pickle_dir):

        head_common='isWeight:{}_numLoser:{}_div:{}_'.format(self.isWeightedByReadSegment, self.NumRandomLosers,self.division)

        self.results_paper.to_pickle(pickle_dir + head_common +'results_paper.pickle')
        self.results_digital.to_pickle(pickle_dir + head_common +'_results_digital.pickle')
        self.elo_rating_paper.to_pickle(pickle_dir + head_common + '_elo_rating_paper_weight.pickle')
        self.elo_rating_digital.to_pickle(pickle_dir + head_common +'_elo_rating_digital_weight.pickle')