# -- 各ファイルで共有される定数値
from os import path

# アンケートファイルの所在
kEnqueteDirectoryBase             = '/home/data/enquete'
kEnqueteDirectoryRaw              = path.join(kEnqueteDirectoryBase, 'raw')
kEnqueteCsvPathComicSalses        = path.join(kEnqueteDirectoryRaw, 'comic_sales.csv')
kEnqueteCsvPathDigitalEnqueteData = path.join(kEnqueteDirectoryRaw, 'digital_enquete_data.csv')
kEnqueteCsvPathPaperEnqueteData   = path.join(kEnqueteDirectoryRaw, 'paper_enquete_data.csv')
kEnqueteCsvPathTitleData          = path.join(kEnqueteDirectoryRaw, 'title_data.csv')

kEnqueteDirectoryPickleCache      = '/home/data/enquete/work/futabanzu/share/pickle'
kEnquetePicklePathComicSalses     = path.join(kEnqueteDirectoryPickleCache, 'comic_sales.pickle')
kEnquetePicklePathDigitalEnqueteData = path.join(kEnqueteDirectoryPickleCache, 'digital_enquete_data.pickle')
kEnquetePicklePathPaperEnqueteData   = path.join(kEnqueteDirectoryPickleCache, 'paper_enquete_data.pickle')
kEnquetePicklePathTitleData          = path.join(kEnqueteDirectoryPickleCache, 'title_data.pickle')
