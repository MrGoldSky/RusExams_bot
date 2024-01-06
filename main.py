import telebot
from telebot import types
from config import BOT_TOKEN


bot = telebot.TeleBot(BOT_TOKEN)

printy = bot.send_message

@bot.message_handler(commands=["start"])
def start(message):
    printy(message.chat.id, f"Привет, {message.from_user.first_name}!")



bot.polling(none_stop=True)