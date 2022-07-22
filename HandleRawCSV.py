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
        #self.head_common='isWeight:{}_numLoser:{}_div:{}_'.format(self.isWeightedByReadSegment, self.NumRandomLosers,self.division)
        self.enquete_data_digital_filtered, self.enquete_data_filtered, self.issue_num_list, self.head_common=\
            funcs.read_raw_csv(save_dir, isWeightedByReadSegment=self.isWeightedByReadSegment, NumRandomLosers=self.NumRandomLosers,\
                division=self.division, kEnqueteTitleMinimumIssue = kEnqueteTitleMinimumIssue)
        print('Initing Done!')
    
    def fit(self):
        results_digital=funcs.TranslateResult(self.enquete_data_digital_filtered,self.isWeightedByReadSegment,self.NumRandomLosers)
        results_paper=funcs.TranslateResult(self.enquete_data_filtered,self.isWeightedByReadSegment,self.NumRandomLosers)
        print('Translating Done!')
        self.elo_rating_digital = funcs.CalcElo(results_digital, self.issue_num_list)
        self.elo_rating_paper = funcs.CalcElo(results_paper, self.issue_num_list)
        print('Fitting Done!')
    def savepickle(self,pickle_dir):
        self.results_paper.to_pickle(pickle_dir + self.head_common +'results_paper.pickle')
        self.results_digital.to_pickle(pickle_dir + self.head_common +'_results_digital.pickle')
        self.elo_rating_paper.to_pickle(pickle_dir + self.head_common + '_elo_rating_paper_weight.pickle')
        self.elo_rating_digital.to_pickle(pickle_dir + self.head_common +'_elo_rating_digital_weight.pickle')