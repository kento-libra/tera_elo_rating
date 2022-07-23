import pandas as pd
import os
import funcs as fn

class HandleRawCSV:
    def __init__(self,
                save_dir,
                kEnqueteTitleMinimumIssue = 10,
                kEnqueteTargetYear = 2021,
                isWeightedByReadSegment=False,
                NumRandomLosers=0,
                division='All'
                ):
        self.isWeightedByReadSegment=isWeightedByReadSegment
        self.NumRandomLosers=NumRandomLosers
        self.division=division
        self.save_dir=save_dir
        self.enquete_data_digital_filtered, self.enquete_data_paper_filtered, self.issue_num_list, self.head_common=\
            fn.read_raw_csv(save_dir, isWeightedByReadSegment=self.isWeightedByReadSegment, NumRandomLosers=self.NumRandomLosers,\
                division=self.division, kEnqueteTitleMinimumIssue = kEnqueteTitleMinimumIssue)
        print('Initing Done!')
    
    def elo(self):
        if os.path.isfile(self.save_dir + self.head_common + 'elo_rating_paper_weight.pickle')\
            and os.path.isfile(self.save_dir + self.head_common +'elo_rating_digital_weight.pickle'):
            self.elo_rating_paper=pd.read_pickle(self.save_dir + self.head_common + 'elo_rating_paper_weight.pickle')
            self.elo_rating_digital=pd.read_pickle(self.save_dir + self.head_common +'elo_rating_digital_weight.pickle')
        else:
            results_digital=fn.TranslateResult(self.enquete_data_digital_filtered,self.isWeightedByReadSegment,self.NumRandomLosers)
            results_paper=fn.TranslateResult(self.enquete_data_paper_filtered,self.isWeightedByReadSegment,self.NumRandomLosers)
            print('Translating Done!')
            self.elo_rating_digital = fn.CalcElo(results_digital, self.issue_num_list)
            self.elo_rating_paper = fn.CalcElo(results_paper, self.issue_num_list)
            print('Fitting Done!')
            self.elo_rating_paper.to_pickle(self.save_dir + self.head_common + 'elo_rating_paper_weight.pickle')
            self.elo_rating_digital.to_pickle(self.save_dir + self.head_common +'elo_rating_digital_weight.pickle')
    
    def EloSheet(self):
        self.elo_rating_paper_sheet=fn.EloToSheet(self.elo_rating_paper,self.issue_num_list).reindex(columns=self.elo_calc_list.columns).interpolate(limit_direction='both')[self.elo_calc_list]
        self.elo_rating_digital_sheet=fn.EloToSheet(self.elo_rating_digital,self.issue_num_list).reindex(columns=self.elo_calc_list.columns).interpolate(limit_direction='both')[self.elo_calc_list]
    
    def votes(self):
        self.votes_paper=fn.CalcVotes(self.enquete_data_paper_filtered, self.issue_num_list).reindex(columns=self.elo_calc_list.columns).interpolate(limit_direction='both')[self.elo_calc_list]
        self.votes_digital=fn.CalcVotes(self.enquete_data_digital_filtered, self.issue_num_list).reindex(columns=self.elo_calc_list.columns).interpolate(limit_direction='both')[self.elo_calc_list]
    
    def save_pickle(self):
        if self.votes_paper is not None and self.votes_digital is not None:
            self.votes_paper.to_pickle(self.save_dir + self.head_common + 'votes_paper.pickle')
            self.votes_digital.to_pickle(self.save_dir + self.head_common + 'votes_digital.pickle')
            print('votes saved!')
        if self.elo_rating_paper_sheet is not None and self.elo_rating_digital_sheet is not None:
            self.elo_rating_paper_sheet.to_pickle(self.save_dir + self.head_common + 'elo_paper_sheet.pickle')
            self.elo_rating_digital_sheet.to_pickle(self.save_dir + self.head_common + 'elo_digital_sheet.pickle')
            print('elo saved!')

    def load_pickle(self):
        try:
            self.votes_paper=pd.read_pickle(self.save_dir + self.head_common + 'votes_paper.pickle')
        except:
            print('{} does not exist'.format(self.save_dir + self.head_common + 'votes_paper.pickle'))
        try:
            self.votes_digital=pd.read_pickle(self.save_dir + self.head_common + 'votes_digital.pickle')
        except:
            print('{} does not exist'.format(self.save_dir + self.head_common + 'votes_digital.pickle'))
        try:
            self.elo_rating_paper_sheet=pd.read_pickle(self.save_dir + self.head_common + 'elo_paper_sheet.pickle')
        except:
            print('{} does not exist'.format(self.save_dir + self.head_common + 'elo_paper_sheet.pickle'))
        try:
            self.elo_rating_digital_sheet=pd.read_pickle(self.save_dir + self.head_common + 'elo_digital_sheet.pickle')
        except:
            print('{} does not exist'.format(self.save_dir + self.head_common + 'elo_digital_sheet.pickle'))
        
    def MakeReference_v1(self):
        elo_rating_digital_frame=pd.DataFrame()
        for issue in self.issue_num_list:
            tmp_df=self.elo_rating_digital.query('issue==@issue')
            tmp_df.index=tmp_df['name']
            elo_rating_digital_frame = pd.concat([elo_rating_digital_frame, tmp_df['elo']],axis=1)
        elo_rating_digital_frame.columns=self.issue_num_list
        elo_rating_digital_frame_filtered = elo_rating_digital_frame.drop([1,'マッシュル-MASHLE-']).T.dropna(axis=1,thresh=30)
        self.elo_calc_list=~elo_rating_digital_frame_filtered.interpolate(limit=2).isna()
        self.elo_calc_list.to_pickle(self.save_dir + self.head_common + 'elo_calc_list_v1.pickle')

    def SetReference(self,ref_name=None):
        if ref_name is not None:
            self.elo_calc_list=pd.read_pickle(self.save_dir + ref_name)
        else:
            self.elo_calc_list=pd.read_pickle(self.save_dir + self.head_common + 'elo_calc_list_v1.pickle')
    def automate(self):
        self.elo()
        self.MakeReference_v1()
        self.votes()
        self.save_pickle()