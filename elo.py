import math
import pandas
import elo_calc
import datetime


def main():
    manga=elo_calc.elo_calc('player.csv','result.csv')
    #manga.debug()
    start_time=datetime.datetime.now()
    manga.fit()
    print(datetime.datetime.now()-start_time)
    #manga.save_rating('elo_dummy.csv')
    #manga.save_move('elo_dummy_mov.png')
if __name__ == '__main__':
    main()
