from inspect import isclass
import pandas as pd
import numpy as np
import random
def win_rate(Ra,Rb):
    return 1/(10**((Rb-Ra)/400)+1)
def generate_result(A,B):
    if random.random() < win_rate(player.at[A,'elo'],player.at[B,'elo']):
        return [A,B]
    return[B,A]
def set_prefer(A,B):
    if '呪術回線' in [A,B] and 'キメツの刃' in [A,B]:
        return 0.5
    if 'ヒロアカ' in [A,B] and 'キメツの刃' in [A,B]:
        return 0.3
    else:
        return 0.2
def main():
    global player
    isClassic=False
    player = pd.DataFrame()
    player['name']=['キメツの刃','呪術回線','ヒロアカ']
    player.to_csv('player.csv',index=False)
    result=pd.DataFrame(columns=['win','lose'])
    result_len=1000000
    #result=result.append(pd.Series(['キメツの刃','ヒロアカ'],index=result.columns),ignore_index=True)
    player['elo']=1500
    player = player.set_index('name')
    player.at['キメツの刃','elo']=1800
    player.at['ヒロアカ','elo']=1400
    if isClassic:
        for i in range(result_len):
            preference=random.random()
            if preference>0.8:
                result=result.append(pd.Series(generate_result('呪術回線','ヒロアカ'),index=result.columns),ignore_index=True)
            elif preference>0.5:
                result=result.append(pd.Series(generate_result('キメツの刃','ヒロアカ'),index=result.columns),ignore_index=True)
            else:
                result=result.append(pd.Series(generate_result('呪術回線','キメツの刃'),index=result.columns),ignore_index=True)
    else:
        for name1 in player.index:
            for name2 in player.index:
                if name1 != name2:
                    tmp=[[name1, name2],]*int(result_len*set_prefer(name1, name2)*win_rate(player.at[name1,'elo'],player.at[name2,'elo']))
                    result=pd.concat([result, pd.DataFrame(tmp, columns=result.columns)])
    print(result)
    result.to_csv('result_{}_N_{}.csv'.format(isClassic,result_len),index=False)
if __name__ == '__main__':
    main()
