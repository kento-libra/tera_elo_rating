import pandas as pd
import numpy as np

def win_rate(Ra,Rb):
    return 1/(10**((Rb-Ra)/400)+1)

class elo_calc:
    def __init__(self,player_dir,result_dir):
        self.C=8
        self.player = pd.read_csv(player_dir)
        self.player = self.player.set_index('name')
        self.result = pd.read_csv(result_dir)
        self.player['elo']=1500.0

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
        print(self.player)
        
    def const_step(self):
        self.C/=2
    def save_rating(self,save_dir):
        self.player.to_csv(save_dir)
