import HandleRawCSV
from constants import kEnqueteEloPickleBase

def main():
    mycsv=HandleRawCSV.HandleRawCSV(kEnqueteEloPickleBase)
    mycsv.elo()
    mycsv.save_pickle(kEnqueteEloPickleBase)

    # myelo=elo_calc.elo_calc('player.csv','result.csv')
    # myelo.fit()
    # print(myelo.player)
if __name__ == '__main__':
    main()
