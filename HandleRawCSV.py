import pandas as pd
import os
import funcs

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
        #self.head_common='isWeight:{}_numLoser:{}_div:{}_'.format(self.isWeightedByReadSegment, self.NumRandomLosers,self.division)
        self.enquete_data_digital_filtered, self.enquete_data_filtered, self.issue_num_list, self.head_common=\
            funcs.read_raw_csv(save_dir, isWeightedByReadSegment=self.isWeightedByReadSegment, NumRandomLosers=self.NumRandomLosers,\
                division=self.division, kEnqueteTitleMinimumIssue = kEnqueteTitleMinimumIssue)
        print('Initing Done!')
    
    def elo(self):
        if os.path.isfile(self.save_dir + self.head_common + 'elo_rating_paper_weight.pickle')\
            and os.path.isfile(self.save_dir + self.head_common +'elo_rating_digital_weight.pickle'):
            self.elo_rating_paper=pd.read_pickle(self.save_dir + self.head_common + 'elo_rating_paper_weight.pickle')
            self.elo_rating_digital=pd.read_pickle(self.save_dir + self.head_common +'elo_rating_digital_weight.pickle')
        else:
            results_digital=funcs.TranslateResult(self.enquete_data_digital_filtered,self.isWeightedByReadSegment,self.NumRandomLosers)
            results_paper=funcs.TranslateResult(self.enquete_data_filtered,self.isWeightedByReadSegment,self.NumRandomLosers)
            print('Translating Done!')
            self.elo_rating_digital = funcs.CalcElo(results_digital, self.issue_num_list)
            self.elo_rating_paper = funcs.CalcElo(results_paper, self.issue_num_list)
            print('Fitting Done!')
            self.elo_rating_paper.to_pickle(self.save_dir + self.head_common + 'elo_rating_paper_weight.pickle')
            self.elo_rating_digital.to_pickle(self.save_dir + self.head_common +'elo_rating_digital_weight.pickle')

    def save_pickle(self):
        pass
    
    def MakeReference_v1(self):
        elo_rating_digital_frame=pd.DataFrame()
        for issue in self.issue_num_list:
            tmp_df=self.elo_rating_digital.query('issue==@issue')
            tmp_df.index=tmp_df['name']
            elo_rating_digital_frame = pd.concat([elo_rating_digital_frame, tmp_df['elo']],axis=1)
        elo_rating_digital_frame.columns=self.issue_num_list
        elo_rating_digital_frame_filtered = elo_rating_digital_frame.drop([1,'マッシュル-MASHLE-']).T.dropna(axis=1,thresh=30)
        self.elo_calc_list=~elo_rating_digital_frame_filtered.interpolate(limit=2).isna()
        self.elo_calc_list.to_pickle(self.save_dir + self.head_common + 'elo_calc_list_v1')