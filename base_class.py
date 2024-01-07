import sqlite3


def connect_to_db(base):
    
    if base == 'user_base':
        path = 'user_base/user_base.sqlite3'
    elif base == 'question4':
        path = 'base/questions/4/question4.sqlite3'
    try:
        con = sqlite3.connect(path)
        cur = con.cursor()
        return con, cur
    except BaseException as e:
        return e
