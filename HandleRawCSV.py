import pandas as pd
import numpy as np
import japanize_matplotlib
from tqdm import tqdm
import matplotlib.pyplot as plt

class HandleRawCSV:
    def __init__(self,
                kEnqueteCsvPathPaperEnqueteData,
                kEnqueteCsvPathDigitalEnqueteData, 
                kEnqueteCsvPathTitleData,
                kEnqueteTitleMinimumIssue = 10,
                kEnqueteTargetYear = 2021,
                isWeightedByReadSegment=False,
                NumRandomLosers=0
                ):
        enquete_data = pd.read_csv(kEnqueteCsvPathPaperEnqueteData)
        enquete_data_digital = pd.read_csv(kEnqueteCsvPathDigitalEnqueteData)
        title_data = pd.read_csv(kEnqueteCsvPathTitleData)
        