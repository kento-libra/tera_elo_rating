from genericpath import isfile
import os
import pandas as pd
import numpy as np
import japanize_matplotlib
import pickle
from tqdm import tqdm
import matplotlib.pyplot as plt
import elo_calc
from constants import kEnqueteCsvPathPaperEnqueteData, kEnqueteCsvPathDigitalEnqueteData, kEnqueteCsvPathTitleData, kEnqueteEloPickleBase


def TranslateResult(enquete_data,isWeightedByReadSegment,NumRandomLosers):
    results = []
    unique_list=[]
    for i in enquete_data['issue'].unique():
        issue_clip=enquete_data.query('issue == {}'.format(i)).loc[:,'title_1':'title_3']
        tmp=issue_clip['title_1']
        tmp=pd.concat([tmp,issue_clip['title_2']])
        tmp=pd.concat([tmp,issue_clip['title_3']])
        issue_unique_list=tmp.unique()
        unique_list.append([issue_unique_list,i])
    unique_list=pd.DataFrame(unique_list, columns=['list','issue'])
    for _, row in tqdm(enquete_data.iterrows(), total=enquete_data.shape[0]):
        i, t1, t2, t3, w = row['issue'], row['title_1'], row['title_2'], row['title_3'], int(row['read_segment']) if isWeightedByReadSegment else 1
        results.extend(int(200000/len(enquete_data)+1)*[
            [i, t1, t2, w],
            [i, t2, t3, w],
            [i, t1, t3, w],
        ])
        if NumRandomLosers is 0:
            continue

        known_list=np.array([t1, t2, t3])
        random_loser_candidate=np.setdiff1d(unique_list[unique_list['issue']==i]['list'].to_list(), known_list)
        random_loser_list = np.random.choice(random_loser_candidate, NumRandomLosers, replace=False)
        for j in range(NumRandomLosers):
            results.extend([
            [i, t1, random_loser_list[j], w],
            [i, t2, random_loser_list[j], w],
            [i, t3, random_loser_list[j], w],
            ])
    results = pd.DataFrame(results, columns=['issue', 'win', 'lose','weight'])
    return results

def CalcElo(results, issue_num_list):
    elo_rating = pd.DataFrame(columns = ['issue', 'name', 'rank', 'elo'])
    for issue in tqdm(issue_num_list):
        results_by_issue = results.query('issue == @issue')[['win', 'lose','weight']]
        results_by_issue.reset_index(drop=True, inplace=True)
        # アンケートに登場するタイトルを抽出
        p_win = results_by_issue.groupby('win').groups.keys()
        p_lose = results_by_issue.groupby('lose').groups.keys()
        p_weight = results_by_issue.groupby('weight').groups.keys()
        players_by_issue = pd.DataFrame(p_win | p_lose | p_weight, columns=['name'])
        # Elo ratingを求める
        elo = elo_calc.elo_calc(players_by_issue, results_by_issue)
        elo.fit()
        # ランキングの計算
        res = elo.player
        res['rank'] = res['elo'].rank(ascending=False, method='min')
        # 週ごとのデータに追加
        res['issue'] = issue
        res.reset_index(inplace=True)
        res = res[['issue', 'name', 'rank', 'elo']]
        elo_rating = elo_rating.append(res, ignore_index=True)
    return elo_rating

def CalcVotes():
    return

filtered_digital_name='digital_filtered_raw.pickle'
filtered_paper_name='paper_filtered_raw.pickle'
issue_num_name='issue_num_list.npy'
def read_raw_csv(save_dir,
                isWeightedByReadSegment=False,
                NumRandomLosers=0,
                division='All',
                kEnqueteTitleMinimumIssue = 10):
    head_common ='isWeight:{}_numLoser:{}_div:{}_'.format(isWeightedByReadSegment, NumRandomLosers, division)
    if os.path.isfile(save_dir + head_common + filtered_digital_name) and os.path.isfile(save_dir + head_common + filtered_paper_name) and os.path.isfile(save_dir + head_common + issue_num_name):
        enquete_data_digital_filtered = pd.read_pickle(save_dir + head_common + filtered_digital_name)
        enquete_data_filtered = pd.read_pickle(save_dir + head_common + filtered_paper_name)
        issue_num_list = np.load(save_dir + head_common + issue_num_name)
    else:
        enquete_data = pd.read_csv(kEnqueteCsvPathPaperEnqueteData)
        enquete_data_digital = pd.read_csv(kEnqueteCsvPathDigitalEnqueteData)
        title_data = pd.read_csv(kEnqueteCsvPathTitleData)
        title_data_only = title_data[['title_code', 'title']]

        enquete_data_merged = pd.merge(enquete_data, title_data_only, left_on='title_1', right_on='title_code', suffixes=['', '_1'])\
                                .drop(columns=['title_code', 'title_1'])\
                                .rename(columns={'title': 'title_1'})
        enquete_data_merged = pd.merge(enquete_data_merged, title_data_only, left_on='title_2', right_on='title_code', suffixes=['', '_2'])\
                                .drop(columns=['title_code', 'title_2'])\
                                .rename(columns={'title': 'title_2'})
        enquete_data_merged = pd.merge(enquete_data_merged, title_data_only, left_on='title_3', right_on='title_code', suffixes=['', '_3'])\
                                .drop(columns=['title_code', 'title_3'])\
                                .rename(columns={'title': 'title_3'})
        # 読み切りなどを削除 'year == @kEnqueteTargetYear'
        if division is not 'All':
            enquete_data_digital=enquete_data_digital.query(division)
            enquete_data_merged=enquete_data_merged.query(division)
        enquete_data_digital_filtered = enquete_data_digital.query('not age.str.contains("\|")')\
                                                    .groupby('title_1')\
                                                    .filter(lambda x: x['issue'].groupby(x['title_1']).nunique().max() >= kEnqueteTitleMinimumIssue)
        enquete_data_digital_filtered.loc[:,'read_segment'] = enquete_data_digital_filtered.loc[:,'read_segment'].replace('全部読んでいる', '25')
        enquete_data_digital_filtered.loc[:,'read_segment'] = enquete_data_digital_filtered.loc[:,'age'].replace('(\d+).*', r'\1',regex=True)
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
        enquete_data_filtered['read_segment']=1
        issue_num_digital = enquete_data_digital_filtered['issue']
        issue_num_paper = enquete_data_filtered['issue']
        issue_num_list = np.intersect1d(issue_num_digital.unique(), issue_num_paper.unique())
        issue_num_list.sort()

        enquete_data_digital_filtered.to_pickle(save_dir + head_common + filtered_digital_name)
        enquete_data_filtered.to_pickle(save_dir + head_common + filtered_paper_name)
        np.save(save_dir + head_common + issue_num_name ,issue_num_list)
    return enquete_data_digital_filtered, enquete_data_filtered, issue_num_list, head_common

def GenerateGroupList(agelist):
    grouplist=[]
    agelist=[-1]+agelist+[100]
    for i in range(len(agelist)-1):
        grouplist.append('{} < age <= {} and gender == 1'.format(agelist[i],agelist[i+1]))
    for i in range(len(agelist)-1):
        grouplist.append('{} < age <= {} and gender == 2'.format(agelist[i],agelist[i+1]))
    return grouplist

