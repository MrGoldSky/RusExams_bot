import os
import telebot
from telebot import types
from base_class import *
import app_logger
from config import BOT_TOKEN



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
    markup.add(choice_questions, bot_info, statistics, top_users)
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
        accepted = cur.execute(f"""SELECT accepted FROM user_base
                                WHERE user_id == {message.chat.id}""").fetchone()[0]
        wrong_answer = cur.execute(f"""SELECT wrong_answer FROM user_base
                                WHERE user_id == {message.chat.id}""").fetchone()[0]
        not_stated = cur.execute(f"""SELECT MAX(id) FROM question4""").fetchone()[0]
        con.close()
    except BaseException as e:
        logger.error(f"Select from table (user_base) ERROR: values=accepted, wrong_answer, not_stated exception={e}")

    printy(message.chat.id, f"""Статистика ЕГЭ №4\n
Решено верно {chr(9989)} {accepted}
Решено неверно {chr(10060)} {wrong_answer}
Не решено {chr(9200)} {not_stated - accepted}""")


bot.polling(none_stop=True)

