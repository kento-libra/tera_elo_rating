import math
import pandas
import elo_calc
import datetime
import HandleRawCSV
from constants import kEnqueteCsvPathPaperEnqueteData, kEnqueteCsvPathDigitalEnqueteData, kEnqueteCsvPathTitleData

def main():
    mycsv=HandleRawCSV.HandleRawCSV(kEnqueteCsvPathPaperEnqueteData, kEnqueteCsvPathDigitalEnqueteData, kEnqueteCsvPathTitleData)
if __name__ == '__main__':
    main()
