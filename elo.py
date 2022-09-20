import HandleRawCSV
import elo_calc
import pandas as pd
#from constants import kEnqueteEloPickleBase

def main():
    myelo=elo_calc.elo_calc(pd.read_csv('player.csv'),pd.read_csv('result_False_N_1000.csv').sample(frac=1, ignore_index=True))
    myelo.fit2()
    print(myelo.player)
if __name__ == '__main__':
    main()
