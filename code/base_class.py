import sqlite3


def connect_to_db():
    try:
        con = sqlite3.connect('data/base/base.sqlite3')
        # con = sqlite3.connect('C:\\Users\Mr_GoldSky_\\Desktop\\RusExams_bot\\data\\base\\base.sqlite3')
        cur = con.cursor()
        return con, cur
    except BaseException as e:
        return e
