import pandas as pd
import os
import funcs as fn

class HandleRawCSV:
    def __init__(self,
                dirs,
                kEnqueteTitleMinimumIssue = 10,
                kEnqueteTargetYear = 2021,
                isWeightedByReadSegment=False,
                NumRandomLosers=0,
                division='All'
                ):
        
        self.isWeightedByReadSegment=isWeightedByReadSegment
        self.NumRandomLosers=NumRandomLosers
        self.division=division
        self.dirs=dirs
        self.enquete_data_digital_filtered, self.enquete_data_paper_filtered, self.issue_num_list, self.head_common=\
            fn.read_raw_csv(dirs, isWeightedByReadSegment=self.isWeightedByReadSegment, NumRandomLosers=self.NumRandomLosers,\
                division=self.division, kEnqueteTitleMinimumIssue = kEnqueteTitleMinimumIssue)
        
        print('Initing Done!')
    
    def elo(self):
        if os.path.isfile(self.dirs['pickle'] + self.head_common + 'elo_rating_paper_list.pickle')\
            and os.path.isfile(self.dirs['pickle'] + self.head_common +'elo_rating_digital_list.pickle'):
            #loading elo list
            self.elo_rating_paper=pd.read_pickle(self.dirs['pickle'] + self.head_common + 'elo_rating_paper_list.pickle')
            self.elo_rating_digital=pd.read_pickle(self.dirs['pickle'] + self.head_common +'elo_rating_digital_list.pickle')
        else:
            results_digital=fn.TranslateResult(self.enquete_data_digital_filtered,self.isWeightedByReadSegment,self.NumRandomLosers)
            results_paper=fn.TranslateResult(self.enquete_data_paper_filtered,self.isWeightedByReadSegment,self.NumRandomLosers)
            print('Translating Done!')
            self.elo_rating_digital = fn.CalcElo(results_digital, self.issue_num_list)
            self.elo_rating_paper = fn.CalcElo(results_paper, self.issue_num_list)
            print('Fitting Done!')

            #saveing elo list
            self.elo_rating_paper.to_pickle(self.dirs['pickle'] + self.head_common + 'elo_rating_paper_list.pickle')
            self.elo_rating_digital.to_pickle(self.dirs['pickle'] + self.head_common +'elo_rating_digital_list.pickle')
    
    def EloSheet(self):
        if os.path.isfile(self.dirs['pickle'] + self.head_common + 'elo_paper_sheet.pickle')\
            and os.path.isfile(self.dirs['pickle'] + self.head_common +'elo_digital_sheet.pickle'):
            self.elo_rating_paper_sheet=pd.read_pickle(self.dirs['pickle'] + self.head_common + 'elo_paper_sheet.pickle')
            self.elo_rating_digital_sheet=pd.read_pickle(self.dirs['pickle'] + self.head_common + 'elo_digital_sheet.pickle')
        else:
            self.elo_rating_paper_sheet=fn.EloToSheet(self.elo_rating_paper,self.issue_num_list).reindex(columns=self.elo_calc_list.columns).interpolate(limit_direction='both')[self.elo_calc_list]
            self.elo_rating_digital_sheet=fn.EloToSheet(self.elo_rating_digital,self.issue_num_list).reindex(columns=self.elo_calc_list.columns).interpolate(limit_direction='both')[self.elo_calc_list]
            
            self.elo_rating_paper_sheet.to_pickle(self.dirs['pickle'] + self.head_common + 'elo_paper_sheet.pickle')
            self.elo_rating_digital_sheet.to_pickle(self.dirs['pickle'] + self.head_common + 'elo_digital_sheet.pickle')

    def votes(self):
        votes_paper_dir=self.dirs['pickle'] + self.head_common + 'votes_paper.pickle'
        votes_digital_dir=self.dirs['pickle'] + self.head_common + 'votes_digital.pickle'
        if os.path.isfile(votes_paper_dir) and os.path.isfile(votes_digital_dir):
            self.votes_paper=pd.read_pickle(votes_paper_dir)
            self.votes_digital=pd.read_pickle(votes_digital_dir)
        else:
            self.votes_paper=fn.CalcVotes(self.enquete_data_paper_filtered, self.issue_num_list).reindex(columns=self.elo_calc_list.columns).interpolate(limit_direction='both')[self.elo_calc_list]
            self.votes_digital=fn.CalcVotes(self.enquete_data_digital_filtered, self.issue_num_list).reindex(columns=self.elo_calc_list.columns).interpolate(limit_direction='both')[self.elo_calc_list]
            self.votes_paper.to_pickle(votes_paper_dir)
            self.votes_digital.to_pickle(votes_digital_dir)        
        self.votetoratio()    
    
    def votetoratio(self):
        self.votes_ratio_paper=(self.votes_paper.T/self.votes_paper.T.sum()).T
        self.votes_ratio_digital=(self.votes_digital.T/self.votes_digital.T.sum()).T   

    def MakeReference_v1(self):
        elo_rating_digital_frame=pd.DataFrame()
        for issue in self.issue_num_list:
            tmp_df=self.elo_rating_digital.query('issue==@issue')
            tmp_df.index=tmp_df['name']
            elo_rating_digital_frame = pd.concat([elo_rating_digital_frame, tmp_df['elo']],axis=1)
        elo_rating_digital_frame.columns=self.issue_num_list
        elo_rating_digital_frame_filtered = elo_rating_digital_frame.drop(['マッシュル-MASHLE-']).T.dropna(axis=1,thresh=30)
        elo_calc_list=~elo_rating_digital_frame_filtered.interpolate(limit=2).isna()
        elo_calc_list.to_pickle(self.dirs['pickle'] + self.head_common + 'elo_calc_list_v1.pickle')

    def SetReference(self, ref_name=None):
        if ref_name is not None:
            self.elo_calc_list=pd.read_pickle(ref_name)
        else:
            self.elo_calc_list=pd.read_pickle(self.dirs['pickle'] + 'isWeight:False_numLoser:0_div:All_elo_calc_list_v1.pickle')
    
    def automate(self,doMakeRef=False, ref_name=None):
        print('Calculating Elo Rating...')
        self.elo()
        if doMakeRef:
            print('Set Matrix as Reference')
            self.MakeReference_v1()
        self.SetReference()
        print('Calculating Voting Ratios...')
        self.votes()
        print('Calculating Elo Rating...')
        self.EloSheet()
