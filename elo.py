import math
import pandas
import elo_calc


def main():
    manga=elo_calc.elo_calc('player.csv','result.csv')
    manga.debug()
    manga.fit()
    #manga.save_rating('elo_dummy.csv')
    #manga.save_move('elo_dummy_mov.png')
if __name__ == '__main__':
    main()
