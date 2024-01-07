import sqlite3


def connect_to_db(self):
    try:
        con = sqlite3.connect("C:/Users/Mr_GoldSky_/Desktop/My_bot/bot_data/My_bot_db.sqlite")
        cur = con.cursor()
        return con, cur
    except BaseException:
        print("Ошибка подключения к БД")
