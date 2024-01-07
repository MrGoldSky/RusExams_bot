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
    printy(message.chat.id, f"Привет, {message.from_user.first_name}!")
    connection = connect_to_db('user_base')
    if len(connection) == 2:
        con, cur = connection[0], connection[1]
        logger.info(f"Connected to datebase(user_base) for userid={message.chat.id}")
    else:
        logger.critical(f"Connection to database(user_base) ERROR: userid={message.chat.id} exception={connection[0]}")
        return
    try:
        cur.execute(f"""INSERT INTO base(user_id, user_name)
                        VALUES ({message.chat.id}, '{message.from_user.first_name}')""")
        con.commit()
        con.close()
    except BaseException as e:
        logger.error(f"Insert to database(user_base) ERROR: values={message.chat.id}, {message.from_user.first_name} exception={e}")


bot.polling(none_stop=True)

