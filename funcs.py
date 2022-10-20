from genericpath import isfile
import os
import pandas as pd
import numpy as np
import japanize_matplotlib
import pickle
from tqdm import tqdm
import matplotlib.pyplot as plt
import elo_calc
import re
#from constants import kEnqueteCsvPathPaperEnqueteData, kEnqueteCsvPathDigitalEnqueteData, kEnqueteCsvPathTitleData, kEnqueteEloPickleBase,kEnqueteEloImgBase


def TranslateResult(enquete_data,isWeightedByReadSegment,NumRandomLosers):
    results = []
    unique_list=[]
    issue_list=enquete_data['issue'].unique()
    issue_list=np.sort(issue_list)
    for i in range(len(issue_list)):
        #print('issue in {}'.format(issue_target))
        issue_clip=enquete_data.query('issue == {}'.format(issue_list[i])).loc[:,'title_1':'title_3']
        #print(issue_clip)
        tmp=issue_clip['title_1']
        tmp=pd.concat([tmp,issue_clip['title_2']])
        tmp=pd.concat([tmp,issue_clip['title_3']])
        issue_unique_list=tmp.unique()
        unique_list.append([issue_unique_list,issue_list[i]])
    unique_list=pd.DataFrame(unique_list, columns=['list','issue'])
    for _, row in tqdm(enquete_data.iterrows(), total=enquete_data.shape[0]):
        issue, t1, t2, t3, w = row['issue'], row['title_1'], row['title_2'], row['title_3'], 1 #int(row['read_segment']) if isWeightedByReadSegment else 1
        results.extend([
            [issue, t1, t2, w],
            [issue, t2, t3, w],
            [issue, t1, t3, w],
        ])
        if NumRandomLosers is 0:
            continue

        known_list=np.array([t1, t2, t3])
        random_loser_candidate=np.setdiff1d(unique_list[unique_list['issue']==i]['list'].to_list(), known_list)
        random_loser_list = np.random.choice(random_loser_candidate, NumRandomLosers, replace=False)
        for j in range(NumRandomLosers):
            results.extend([
            [issue, t1, random_loser_list[j], w],
            [issue, t2, random_loser_list[j], w],
            [issue, t3, random_loser_list[j], w],
            ])
    results = pd.DataFrame(results, columns=['issue', 'win', 'lose','weight'])
    return results

def CalcElo(results, issue_num_list):
    results=results.query('win != 1 and lose != 1')
    elo_rating = pd.DataFrame(columns = ['issue', 'name', 'rank', 'elo'])
    issue_num_list=np.sort(issue_num_list)
    
    for i in tqdm(range(len(issue_num_list))):
        stride=1
        issue_target=list(issue_num_list[max(0,i-int(stride/2)):min(len(issue_num_list), i+int((stride+1)/2))])
        results_by_issue = results.query('issue in {}'.format(issue_target))[['win', 'lose','weight']]
        results_by_issue.reset_index(drop=True, inplace=True)
        # アンケートに登場するタイトルを抽出
        p_win = results_by_issue.groupby('win').groups.keys()
        p_lose = results_by_issue.groupby('lose').groups.keys()
        p_weight = results_by_issue.groupby('weight').groups.keys()
        players_by_issue = pd.DataFrame(p_win | p_lose | p_weight, columns=['name']).query('name != 1')
        #print(players_by_issue)
        # Elo ratingを求める
        elo = elo_calc.elo_calc(players_by_issue, results_by_issue)
        elo.fit()
        # ランキングの計算
        res = elo.player
        res['rank'] = res['elo'].rank(ascending=False, method='min')
        # 週ごとのデータに追加
        res['issue'] = issue_num_list[i]
        res.reset_index(inplace=True)
        res = res[['issue', 'name', 'rank', 'elo']]
        elo_rating = elo_rating.append(res, ignore_index=True)
    return elo_rating

def EloToSheet(elo_rating, issue_num_list):
    elo_rating_frame=pd.DataFrame()
    for issue in issue_num_list:
        tmp_df=elo_rating.query('issue==@issue')
        tmp_df.index=tmp_df['name']
        elo_rating_frame = pd.concat([elo_rating_frame, tmp_df['elo']],axis=1)
    elo_rating_frame.columns=issue_num_list
    elo_rating_sheet=elo_rating_frame.T
    return elo_rating_sheet

def CalcVotes(enquete_data, issue_num_list):
  result_list=[]
  for i in issue_num_list:
    flatten_list=enquete_data.query('issue==@i').loc[:,'title_1':'title_3'].to_numpy().flatten()
    titles, num_votes=np.unique(flatten_list,return_counts=True)
    result_list.append(pd.DataFrame(num_votes,index=titles,columns=[i]))
  return pd.concat(result_list,axis=1).T

filtered_digital_name='digital_filtered_raw.pickle'
filtered_paper_name='paper_filtered_raw.pickle'
issue_num_name='issue_num_list.npy'
def read_raw_csv(dirs,
                isWeightedByReadSegment=False,
                NumRandomLosers=0,
                division='All',
                kEnqueteTitleMinimumIssue = 10):
    head_common ='isWeight:{}_numLoser:{}_div:{}_'.format(isWeightedByReadSegment, NumRandomLosers, division)
    print('Calculating: {}'.format(head_common))
    if os.path.isfile(dirs['pickle'] + head_common + filtered_digital_name) and os.path.isfile(dirs['pickle'] + head_common + filtered_paper_name) and os.path.isfile(dirs['pickle'] + head_common + issue_num_name):
        enquete_data_digital_filtered = pd.read_pickle(dirs['pickle'] + head_common + filtered_digital_name)
        enquete_data_filtered = pd.read_pickle(dirs['pickle'] + head_common + filtered_paper_name)
        issue_num_list = np.load(dirs['pickle'] + head_common + issue_num_name)
    else:
        enquete_data = pd.read_csv(dirs['paper'])
        enquete_data_digital = pd.read_csv(dirs['digital'])
        title_data = pd.read_csv(dirs['title'])
        title_data_only = title_data[['title_code', 'title']]
        #print(dirs['paper'])
        if dirs['paper']=='/home/data/enquete/work/tera/raw/paper_enquete_data.csv':
            enquete_data_merged = pd.merge(enquete_data, title_data_only, left_on='title_1', right_on='title_code', suffixes=['', '_1'])\
                                    .drop(columns=['title_code', 'title_1'])\
                                    .rename(columns={'title': 'title_1'})
            enquete_data_merged = pd.merge(enquete_data_merged, title_data_only, left_on='title_2', right_on='title_code', suffixes=['', '_2'])\
                                    .drop(columns=['title_code', 'title_2'])\
                                    .rename(columns={'title': 'title_2'})
            enquete_data_merged = pd.merge(enquete_data_merged, title_data_only, left_on='title_3', right_on='title_code', suffixes=['', '_3'])\
                                    .drop(columns=['title_code', 'title_3'])\
                                    .rename(columns={'title': 'title_3'})
        else:
            enquete_data_merged=enquete_data
        # 読み切りなどを削除 'year == @kEnqueteTargetYear'
        
        enquete_data_digital_filtered = enquete_data_digital.query('not age.str.contains("\|")')\
                                                    .groupby('title_1')\
                                                    .filter(lambda x: x['issue'].groupby(x['title_1']).nunique().max() >= kEnqueteTitleMinimumIssue)
        #enquete_data_digital_filtered.loc[:,'read_segment'] = enquete_data_digital_filtered.loc[:,'read_segment'].replace('全部読んでいる', '25')
        #enquete_data_digital_filtered.loc[:,'read_segment'] = enquete_data_digital_filtered.loc[:,'age'].replace('(\d+).*', r'\1',regex=True)
        enquete_data_digital_filtered.loc[:,'age'] = enquete_data_digital_filtered.loc[:,'age'].replace('(\d+).*', r'\1',regex=True)
        enquete_data_filtered = enquete_data_merged\
                                        .groupby('title_1')\
                                        .filter(lambda x: x['issue'].groupby(x['title_1']).nunique().max() >= kEnqueteTitleMinimumIssue)
        players_1 = enquete_data_filtered.groupby('title_1').groups.keys()
        players_2 = enquete_data_filtered.groupby('title_2').groups.keys()
        players_3 = enquete_data_filtered.groupby('title_3').groups.keys()
        players_d1 = enquete_data_digital_filtered.groupby('title_1').groups.keys()
        players_d2 = enquete_data_digital_filtered.groupby('title_2').groups.keys()
        players_d3 = enquete_data_digital_filtered.groupby('title_3').groups.keys()

        all_players = players_1 | players_2 | players_3 | players_d1 | players_d2 | players_d3

        players = pd.DataFrame(all_players, columns=['name'])
        players = players.set_index('name')
        enquete_data_digital_filtered['issue']=(enquete_data_digital_filtered['year'].astype(str)+enquete_data_digital_filtered['issue'].astype(str).str.zfill(2)).astype(int)
        enquete_data_filtered['issue']=(enquete_data_filtered['year'].astype(str)+enquete_data_filtered['issue'].astype(str).str.zfill(2)).astype(int)
        enquete_data_filtered=enquete_data_filtered.dropna(subset=['title_1','title_2','title_3'])
        #enquete_data_filtered['read_segment']=1
        enquete_data_digital_filtered=enquete_data_digital_filtered.dropna(subset=['title_1','title_2','title_3','gender','age'])
        enquete_data_digital_filtered=enquete_data_digital_filtered.replace({'gender':{'男性':1,'女性':2}})
        enquete_data_digital_filtered['age']=enquete_data_digital_filtered['age'].astype(int)
        if division is not 'All':
            enquete_data_digital_filtered=enquete_data_digital_filtered.query(division)
            enquete_data_filtered=enquete_data_filtered.query(division)
        issue_num_digital = enquete_data_digital_filtered['issue']
        issue_num_paper = enquete_data_filtered['issue']
        issue_num_list = np.intersect1d(issue_num_digital.unique(), issue_num_paper.unique())
        issue_num_list.sort()

        enquete_data_digital_filtered.to_pickle(dirs['pickle'] + head_common + filtered_digital_name)
        enquete_data_filtered.to_pickle(dirs['pickle'] + head_common + filtered_paper_name)
        np.save(dirs['pickle'] + head_common + issue_num_name ,issue_num_list)
    return enquete_data_digital_filtered, enquete_data_filtered, issue_num_list, head_common

def GenerateGroupList(agelist):
    grouplist=[]
    agelist=[-1]+agelist+[100]
    for i in range(len(agelist)-1):
        grouplist.append('{} < age <= {} and gender == 1'.format(agelist[i],agelist[i+1]))
    for i in range(len(agelist)-1):
        grouplist.append('{} < age <= {} and gender == 2'.format(agelist[i],agelist[i+1]))
    return grouplist

def print_graph(HR_paper, HR_digital, imgs_dir, target='elo', whetherprint=True, appendix=''):
    label_marker=pd.read_csv('/home/data/enquete/work/tera/raw/label_marker.csv', index_col=0)
    #print(label_marker)
    elo_vector=pd.DataFrame()
    if target=='elo':
        print_list=[HR_paper.elo_rating_paper_sheet,HR_digital.elo_rating_digital_sheet]
    if target=='votes_ratio':
        print_list=[HR_paper.votes_ratio_paper,HR_digital.votes_ratio_digital]
    for i in range(len(print_list)):
        tmp_sr=pd.Series(print_list[i].to_numpy().flatten())
        elo_vector=pd.concat([elo_vector,tmp_sr],axis=1)
    elo_corr=elo_vector.iloc[:,[0,1]].corr().iloc[0,1]

    plt.figure(figsize=(6, 6))
    if target=='elo':
        plt.xlim([1200,2000])
        plt.ylim([1200,2000])
        plt.text(1800,1950,'r = {:5f}'.format(elo_corr))
    if target=='votes_ratio':
        plt.xlim([0,0.3])
        plt.ylim([0,0.3])
        plt.text(0.23,0.28,'r = {:5f}'.format(elo_corr))
    plt.xlabel(target+' paper')
    plt.ylabel(target+' digital')
    
    for i in range(len(print_list[0].columns)):
        label_name=print_list[0].iloc[:,i].name
        #print(label_name)
        color_name=np.array(re.split(' +',label_marker[label_name]['c'][1:-1])[:3]).astype('float')
        plt.scatter(print_list[0].iloc[:,i], print_list[1].iloc[:,i], label=label_name, marker=label_marker[label_name]['m'], color=color_name )
    plt.legend(bbox_to_anchor=(1, 0), loc='lower right', borderaxespad=1, fontsize=5)
    if whetherprint:
        save_file_name=imgs_dir+'isWeight:{}_numLoser:{}_paperdiv:{}_digital_div:{}_{}.png'.format(HR_paper.isWeightedByReadSegment, HR_paper.NumRandomLosers,HR_paper.division,HR_digital.division,appendix)
        plt.savefig(save_file_name, format="png", dpi=300)
        print(save_file_name)