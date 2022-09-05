import pandas as pd
import numpy as np
import japanize_matplotlib
import matplotlib.pyplot as plt
from tqdm import tqdm

def win_rate(Ra,Rb):
    return 1/(10**((Rb-Ra)/400)+1)

class elo_calc:
    def __init__(self,player: pd.DataFrame, result: pd.DataFrame):
        self.C=32.0
        self.speed=2
        self.player = player
        self.player = self.player.set_index('name')
        self.result = result
        #self.result_sheet
        self.player['elo']=1500.0
        self.history = self.player['elo']
        self.N = len(self.result.index)

    def debug(self):
        print(self.player)
        print(self.result)
        print(win_rate(1700,1500))

    def fit(self):
        for i in range(self.result.shape[0]):
            winner=self.result.at[i,'win']
            loser=self.result.at[i,'lose']
            delta_rate=self.C*win_rate(self.player.at[loser,'elo'],self.player.at[winner,'elo'])
            #print(delta_rate)
            self.player.at[winner,'elo']+=delta_rate
            self.player.at[loser,'elo']-=delta_rate
            #self.history = pd.concat([self.history,self.player['elo']],axis=1)
            if self.speed*i/self.N > 1/self.C:
                self.const_step()
        #print(self.player)
        #print(self.history)

    def fit2(self):
        player_list=self.player.index.tolist()
        print(player_list)
        result_sheet=pd.DataFrame(index=player_list,columns=player_list)
        result_sheet.fillna(0, inplace=True)
        for i in range(len(self.result)):
            result_sheet[self.result['win'][i]][self.result['lose'][i]]+=1
        p=pd.Series([1.0]*len(player_list),index=player_list)
        p_n=pd.Series([1.0]*len(player_list),index=player_list)
        for _ in range(30):
            for i in range(len(p)):
                division=0.0
                for j in range(len(p)):
                    if i != j:
                        division += (result_sheet[player_list[i]][player_list[j]]+result_sheet[player_list[j]][player_list[i]])/(p[i]+p[j])
                p_n[i]=result_sheet[player_list[i]].sum()/division
            p_n = p_n/p_n.sum()
            p=p_n
        elo_raw=400*np.log10(p_n)
        self.player['elo']=1500+elo_raw-elo_raw.mean()
    def const_step(self):
        self.C/=2
        #print(self.C)
    def save_rating(self,save_dir):
        self.player.to_csv(save_dir)
    def save_move(self,save_dir):
        self.history.T.reset_index(drop=True).plot()
        plt.savefig(save_dir)
