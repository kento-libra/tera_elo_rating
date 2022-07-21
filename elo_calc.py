import pandas as pd
import numpy as np
import japanize_matplotlib
import matplotlib.pyplot as plt

def win_rate(Ra,Rb):
    return 1/(10**((Rb-Ra)/400)+1)

class elo_calc:
    def __init__(self,player: pd.DataFrame, result: pd.DataFrame):
        self.C=32.0
        self.speed=2
        self.player = player
        self.player = self.player.set_index('name')
        self.result = result
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

    def const_step(self):
        self.C/=2
        #print(self.C)
    def save_rating(self,save_dir):
        self.player.to_csv(save_dir)
    def save_move(self,save_dir):
        self.history.T.reset_index(drop=True).plot()
        plt.savefig(save_dir)
