import pandas as pd
import numpy as np
import japanize_matplotlib
import pickle
from tqdm import tqdm
import matplotlib.pyplot as plt
import elo_calc


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
    for issue in tqdm(set(issue_num_list)):
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

def read_csv():
    return