import pandas as pd
import numpy as np
import random
def win_rate(Ra,Rb):
    return 1/(10**((Rb-Ra)/400)+1)
def generate_result(A,B):
    if random.random() < win_rate(player.at[A,'elo'],player.at[B,'elo']):
        return [A,B]
    return[B,A]
def main():
    global player
    player = pd.DataFrame()
    player['name']=['キメツの刃','呪術回線','ヒロアカ']
    player.to_csv('player.csv',index=False)
    result=pd.DataFrame(columns=['win','lose'])
    result_len=9000
    #result=result.append(pd.Series(['キメツの刃','ヒロアカ'],index=result.columns),ignore_index=True)
    player['elo']=1500
    player = player.set_index('name')
    player.at['キメツの刃','elo']=1800
    player.at['ヒロアカ','elo']=1400
    for i in range(result_len):
        preference=random.random()
        if preference>0.8:
            result=result.append(pd.Series(generate_result('呪術回線','ヒロアカ'),index=result.columns),ignore_index=True)
        elif preference>0.5:
            result=result.append(pd.Series(generate_result('キメツの刃','ヒロアカ'),index=result.columns),ignore_index=True)
        else:
            result=result.append(pd.Series(generate_result('呪術回線','キメツの刃'),index=result.columns),ignore_index=True)
    print(result)
    result.to_csv('result.csv',index=False)
if __name__ == '__main__':
    main()
