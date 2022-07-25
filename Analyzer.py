import HandleRawCSV as hr
import pandas as pd
import matplotlib.pyplot as plt
from tqdm import tqdm
import numpy as np
import funcs as fn

class Analyzer():
    def __init__(self,
                save_dir,
                agelist,
                isWeightedByReadSegment=False,
                NumRandomLosers=0,
                division='All',
                ) -> None:
        self.isWeightedByReadSegment=isWeightedByReadSegment
        self.NumRandomLosers=NumRandomLosers
        self.division=division
        self.save_dir=save_dir

        self.allin=hr.HandleRawCSV(save_dir)
        self.allin.automate(doMakeRef=True)

        grouplist=fn.GenerateGroupList(agelist)
        self.HR_list=[]
        #print(grouplist)
        for division in grouplist:
            group_tmp=hr.HandleRawCSV(save_dir, division=division)
            group_tmp.automate()
        self.HR_list.append(group_tmp)
    
