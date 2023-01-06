import token_file
import telebot
from telebot import types

from db import BotDB

BotDB = BotDB('anecdots.db')

bot = telebot.TeleBot(token_file.TOKEN)


@bot.message_handler(commands=['start', 'menu'])
def handle_start(message):
    if (not BotDB.user_exists(message.from_user.id)):
        BotDB.add_user(message.from_user.id)

    btn1 = types.KeyboardButton("Травануть анекдотик")
    btn2 = types.KeyboardButton("Добавить анекдотик")
    markup = types.ReplyKeyboardMarkup(
        resize_keyboard=True, row_width=2).add(btn1).add(btn2)

    bot.send_message(message.chat.id, text="Привет, {0.first_name}!".format(
        message.from_user), reply_markup=markup)


@bot.message_handler(content_types=['text'])
def func(message):
    if (message.text == "Травануть анекдотик"):
        bot.send_message(message.chat.id, text=BotDB.get_record())
    elif (message.text == "Добавить анекдотик"):
        send = bot.send_message(
            message.chat.id, text="Напиши свой юморной анекдот")
        bot.register_next_step_handler(send, add_db)
    else:
        bot.send_message(
            message.chat.id, text="Выбери одно из двух")


def add_db(message):
    if (message.text == "Травануть анекдотик" or message.text == "Добавить анекдотик"):
        bot.send_message(
            message.chat.id, text="Такие анекдотики мы уже знаем :(")
    else:
        BotDB.add_record(message.from_user.id, message.text)
        bot.reply_to(message, "Анекдот добавлен!")


bot.polling(none_stop=True)
