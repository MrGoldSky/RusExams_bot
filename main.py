import os
import telebot
from telebot import types
from base_class import *
import app_logger
from config import BOT_TOKEN
import random


bot = telebot.TeleBot(BOT_TOKEN)

printy = bot.send_message

# logging.debug("A DEBUG Message")
# logging.info("An INFO")
# logging.warning("A WARNING")
# logging.error("An ERROR")
# logging.critical("A message of CRITICAL severity")
cwd = os.getcwd()
os.chdir(f'logs')
logger = app_logger.get_logger(__name__)
os.chdir(cwd)
logger.info('Logger successfully installed')
logger.info("Starting bot")


@bot.message_handler(commands=["start"])
def start(message):
    connection = connect_to_db()
    if len(connection) == 2:
        con, cur = connection[0], connection[1]
        logger.info(f"Connected to datebase(base) for userid={message.chat.id}")
    else:
        logger.critical(f"Connection to database(base) ERROR: userid={message.chat.id} exception={connection[0]}")
    try:
        cur.execute(f"""INSERT INTO user_base(user_id, user_name)
                        VALUES ({message.chat.id}, '{message.from_user.first_name}')""")
        con.commit()
        con.close()
    except BaseException as e:
        if str(e).startswith("UNIQUE"):
            logger.info(f"Connection to database(base): restarting bot for userid={message.chat.id}")
        else:
            logger.error(f"Insert to table(user_base) ERROR: values={message.chat.id}, {message.from_user.first_name} exception={e}")
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)

    bot_info = types.KeyboardButton(f"{chr(8252)}Информация о боте{chr(8252)}")
    choice_questions = types.KeyboardButton(f"{chr(128290)}Выбор номера ЕГЭ{chr(128290)}")
    statistics = types.KeyboardButton(f"{chr(128161)}Статистика{chr(128161)}")
    top_users = types.KeyboardButton(f"{chr(128175)}Топ пользователей{chr(128175)}")
    start_solve = types.KeyboardButton(f"Начать решать!")
    markup.add(choice_questions, bot_info, statistics, top_users, start_solve)
    printy(message.chat.id, f"Привет, {message.from_user.first_name}!")
    printy(message.chat.id, "Возможности бота:", reply_markup=markup)


@bot.message_handler(func=lambda message: message.text == f"{chr(8252)}Информация о боте{chr(8252)}")
def information(message):
    logger.debug(f"Reply information for userid={message.chat.id}")
    printy(message.chat.id, f"Привет, {message.from_user.first_name}!\nДанный бот создан для подготовки к ЕГЭ по Русскому языку.")
    printy(message.chat.id, "Создатель бота: https://t.me/Mr_GoldSky")


@bot.message_handler(func=lambda message: message.text == f"{chr(128161)}Статистика{chr(128161)}")
def statistics(message):
    logger.debug(f"Reply statistics for userid={message.chat.id}")
    connection = connect_to_db()
    if len(connection) == 2:
        con, cur = connection[0], connection[1]
        logger.info(f"Connected to datebase(base) for userid={message.chat.id}")
    else:
        logger.critical(f"Connection to database(base) ERROR: userid={message.chat.id} exception={connection[0]}")
    try:

        accepted = len(cur.execute(f"""SELECT id FROM solved
                                WHERE user_id == {message.chat.id} AND solved == 1""").fetchall())
        wrong_answer = len(cur.execute(f"""SELECT id FROM solved
                                WHERE user_id == {message.chat.id} AND solved == 0""").fetchall())
        not_stated = cur.execute(f"""SELECT MAX(id) FROM question4""").fetchone()[0]
        con.close()
    except BaseException as e:
        logger.error(f"Select from table (solved, question4) ERROR: values=accepted, wrong_answer, not_stated exception={e}")

    printy(message.chat.id, f"""Статистика ЕГЭ №4\n
Решено верно {chr(9989)} {accepted}
Решено неверно {chr(10060)} {wrong_answer}
Не решено {chr(9200)} {not_stated - accepted}""")


@bot.message_handler(func=lambda message: message.text == f"Начать решать!")
def solve(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)

    not_solved = types.KeyboardButton(f"Решать нерешенные")
    solved = types.KeyboardButton(f"Повторить решенные")
    solve_any = types.KeyboardButton(f"Решать любые")
    markup.add(not_solved, solve_any, solved)
    printy(message.chat.id, "Что решаем?):", reply_markup=markup)
    printy(message.chat.id, "Напиши: Стоп чтобы выйти из режима экзамена")


@bot.message_handler(func=lambda message: message.text == f"Решать любые")
def start_solve_any(message):
    logger.debug(f"Reply solve(any) for userid={message.chat.id}")
    connection = connect_to_db()
    if len(connection) == 2:
        con, cur = connection[0], connection[1]
        logger.info(f"Connected to datebase(base) for userid={message.chat.id}")
    else:
        logger.critical(f"Connection to database(base) ERROR: userid={message.chat.id} exception={connection[0]}")
    try:
        ids = cur.execute(f"""SELECT id FROM question4""").fetchall()
        solve_id = random.choice(ids)[0]
        task = cur.execute(f"""SELECT task FROM question4 
                               WHERE id == {solve_id}""").fetchone()[0]

        correct = cur.execute(f"""SELECT correct FROM question4
                                  WHERE id == {solve_id}""").fetchone()[0]
        con.close()
    except BaseException as e:
        logger.error(f"Select from table (question4) ERROR: user_id={message.chat.id} values= ids, task, correct exception={e}")

    bot.register_next_step_handler(printy(message.chat.id, f'{task}'), check, correct, "any", solve_id)


def check(message, correct: str, type_solve: str, solve_id: int):
    logger.debug(f'Checking for userid={message.chat.id} user_input={message.text}, correct={correct}')
    connection = connect_to_db()
    if len(connection) == 2:
        con, cur = connection[0], connection[1]
        logger.info(f"Connected to datebase(base) for userid={message.chat.id}")
    else:
        logger.critical(f"Connection to database(base) ERROR: userid={message.chat.id} exception={connection[0]}")
    if message.text == "Стоп":
        start(message)
        return
    if message.text == correct:
        logger.debug(str(solve_id))
        try:
            if len(cur.execute(f"SELECT solved FROM solved WHERE task_id == {solve_id} AND user_id == {message.chat.id}").fetchall()):
                cur.execute(f"""UPDATE solved SET solved = 1 WHERE task_id == {solve_id} AND user_id == {message.chat.id}""")
            else:
                cur.execute(f"""INSERT INTO solved(user_id, task_id, solved) 
                            VALUES ({message.chat.id}, {solve_id}, 1) """)
            con.commit()
            con.close()
        except BaseException as e:
            logger.error(f"UPDATE table (solved) ERROR: values=solve_id, task_id, correct exception={e}")
        printy(message.chat.id, f"{chr(128077)}")
    else:
        try:            
            if len(cur.execute(f"SELECT solved FROM solved WHERE task_id == {solve_id} AND user_id == {message.chat.id}").fetchall()):
                cur.execute(f"""UPDATE solved SET solved = 0 WHERE task_id == {solve_id} AND user_id == {message.chat.id}""")
            else:
                cur.execute(f"""INSERT INTO solved(user_id, task_id, solved) 
                            VALUES ({message.chat.id}, {solve_id}, 0) """)
            con.commit()
            con.close()
        except BaseException as e:
            logger.error(f"UPDATE table (user_base) ERROR: values=solve_id, task, correct exception={e}")

        printy(message.chat.id, f"{chr(128078)}")
    if type_solve == 'any':
        start_solve_any(message)

bot.polling(none_stop=True)

