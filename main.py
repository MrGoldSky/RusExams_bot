import os
import telebot
from telebot import types
from base_class import *
import app_logger
from config import BOT_TOKEN
import random


bot = telebot.TeleBot(BOT_TOKEN)

printy = bot.send_message

cwd = os.getcwd()
# os.chdir(f'logs')
os.chdir('C:\\Users\\Mr_GoldSky_\\Desktop\\RusExams_bot\\logs')
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
        cur.execute(f"""INSERT INTO user_base(user_id, user_name, username)
                        VALUES ({message.chat.id}, '{message.from_user.first_name}', '{message.from_user.username}')""")
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
    markup.add(not_solved, solved, solve_any)
    printy(message.chat.id, """Ударения ставь используя большую букву (трубопровОд).\n
Учти, что все остальные буквы должны быть ПРОПИСНЫЕ.\n
Чтобы закончить- напиши: Стоп""", reply_markup=markup)


@bot.message_handler(func=lambda message: message.text == f"Решать любые")
def start_solve_any(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(types.KeyboardButton(f"Стоп"))
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

    bot.register_next_step_handler(printy(message.chat.id, f'{task}', reply_markup=markup), check, correct, "any", solve_id)


def check(message, correct: str, type_solve: str, solve_id: int):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(types.KeyboardButton(f"Стоп"))
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
        printy(message.chat.id, f"{chr(128077)}", reply_markup=markup)
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
        printy(message.chat.id, f"{correct.lower()} - {correct}", reply_markup=markup)
    if type_solve == 'any':
        start_solve_any(message)


@bot.message_handler(func=lambda message: message.text == f"{chr(128175)}Топ пользователей{chr(128175)}")
def top(message):
    logger.debug(f"Reply top for userid={message.chat.id}")
    connection = connect_to_db()
    if len(connection) == 2:
        con, cur = connection[0], connection[1]
        logger.info(f"Connected to datebase(base) for userid={message.chat.id}")
    else:
        logger.critical(f"Connection to database(base) ERROR: userid={message.chat.id} exception={connection[0]}")
    try:
        current_top = []

        for user_id in cur.execute(f"""SELECT DISTINCT user_id FROM solved""").fetchall():
            current_accepted = len(cur.execute(f"""SELECT id FROM solved
                                    WHERE user_id == {user_id[0]} AND solved == 1""").fetchall())
            current_wrong_answer = len(cur.execute(f"""SELECT id FROM solved
                                    WHERE user_id == {user_id[0]} AND solved == 0""").fetchall())
            current_username = cur.execute(f"""SELECT username FROM user_base
                                    WHERE user_id == {user_id[0]}""").fetchone()[0]
            current_name = cur.execute(f"""SELECT user_name FROM user_base
                                    WHERE user_id == {user_id[0]}""").fetchone()[0]
            current_not_stated = cur.execute(f"""SELECT MAX(id) FROM question4""").fetchone()[0] - current_accepted - current_wrong_answer
            current_top.append({"user_id": user_id[0], "current_accepted": current_accepted, "current_wrong_answer": current_wrong_answer, 
                                "current_not_stated": current_not_stated, "username": current_username, 'name': current_name})
        con.close()
    except BaseException as e:
        logger.error(f"Select from table (solved) ERROR: values=user_id exception={e}")
    current_top = sorted(current_top, key=lambda x:(-x['current_accepted'], x['current_not_stated'], x['current_wrong_answer']))
    text = f"Топ пользователей по решению\!\n"
    
    if len(current_top) < 3:
        n = len(current_top)
    else:
        n = 3
    rewards = {1:129351, 2:129352, 3:129353}
    for i in range(n):
        text += f'{chr(rewards[i + 1])} [{current_top[i]["name"]}](https://t.me/{current_top[i]["username"]})\n'
        text += f'Решено верно{chr(9989)}: {current_top[i]["current_accepted"]} Решено неверно{chr(10060)}: {current_top[i]["current_wrong_answer"]}\n'
    printy(message.chat.id, text, parse_mode='MarkdownV2', disable_web_page_preview=True)


bot.polling(none_stop=True)

