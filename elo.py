import math
import pandas
import elo_calc
import datetime
import HandleRawCSV
from constants import kEnqueteCsvPathPaperEnqueteData, kEnqueteCsvPathDigitalEnqueteData, kEnqueteCsvPathTitleData

def main():
    #mycsv=HandleRawCSV.HandleRawCSV(kEnqueteCsvPathPaperEnqueteData, kEnqueteCsvPathDigitalEnqueteData, kEnqueteCsvPathTitleData)
    myelo=elo_calc.elo_calc('player.csv','result.csv')
    myelo.fit()
    print(myelo.player)
if __name__ == '__main__':
    main()
