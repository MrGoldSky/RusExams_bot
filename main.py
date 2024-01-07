import telebot
from telebot import types
from config import BOT_TOKEN
from datetime import datetime
from base_class import *
import logging
import os
import app_logger


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

logger.info("Starting bot")

@bot.message_handler(commands=["start"])
def start(message):

    printy(message.chat.id, f"Привет, {message.from_user.first_name}!")
    



bot.polling(none_stop=True)