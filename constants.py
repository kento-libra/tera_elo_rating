# -- 各ファイルで共有される定数値
from os import path



# アンケートファイルの所在
def dir_old():
    kEnqueteDirectoryBase             = '/home/data/enquete'
    kEnqueteDirectoryRaw              = path.join(kEnqueteDirectoryBase, 'raw')
    ComicSalses        = path.join(kEnqueteDirectoryRaw, 'comic_sales.csv')
    DigitalEnqueteData = path.join(kEnqueteDirectoryRaw, 'digital_enquete_data.csv')
    PaperEnqueteData   = path.join(kEnqueteDirectoryRaw, 'paper_enquete_data.csv')
    TitleData          = path.join(kEnqueteDirectoryRaw, 'title_data.csv')
    PickleBase ='/home/data/enquete/work/tera/pickle/'
    ImgBase='/home/data/enquete/work/tera/imgs/'
    return {'sales': ComicSalses,'digital':DigitalEnqueteData,'paper':PaperEnqueteData,\
        'title':TitleData,'pickle':PickleBase, 'img':ImgBase}
def dir_new():
    kEnqueteDirectoryBase             = '/home/data/enquete'
    kEnqueteDirectoryRaw              = path.join(kEnqueteDirectoryBase, 'raw2')
    ComicSalses        = path.join(kEnqueteDirectoryRaw, 'タイトル巻数別売上資料.xlsx')
    DigitalEnqueteData = path.join(kEnqueteDirectoryRaw, 'デジタルアンケート2022年18号以降.csv')
    PaperEnqueteData   = path.join(kEnqueteDirectoryRaw, '紙アンケート5000件.csv')
    TitleData          = path.join(kEnqueteDirectoryRaw, 'title_data.csv')
    PickleBase ='/home/data/enquete/work/tera/pickle2/'
    ImgBase='/home/data/enquete/work/tera/imgs2/'
    return {'sales': ComicSalses,'digital':DigitalEnqueteData,'paper':PaperEnqueteData,\
        'title':TitleData,'pickle':PickleBase, 'img':ImgBase}

