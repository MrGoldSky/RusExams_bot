import sqlite3


def connect_to_db():
    try:
        con = sqlite3.connect('base/base.sqlite3')
        cur = con.cursor()
        return con, cur
    except BaseException as e:
        return e
