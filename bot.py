import token_file
import telebot
import glob
import random
from telebot import types
from PIL import Image
import os as os

from db import BotDB

BotDB = BotDB('anecdots.db')

bot = telebot.TeleBot(token_file.TOKEN)

name_of_buttons = ["Получить смешнявку", "Добавить смешнявку", "Анекдоты",
                   "Мемы", "Травануть анекдотик", "Добавить анекдотик", "⬅️Назад"]


@bot.message_handler(commands=['start', 'menu'])
def handle_start(message):
    if (not BotDB.user_exists(message.from_user.id)):
        BotDB.add_user(message.from_user.id)

    btn1 = types.KeyboardButton("Анекдоты")
    btn2 = types.KeyboardButton("Мемы")
    markup = types.ReplyKeyboardMarkup(
        resize_keyboard=True, row_width=2).add(btn1).add(btn2)

    bot.send_message(message.chat.id, text="Привет, {0.first_name}!".format(
        message.from_user), reply_markup=markup)


@bot.message_handler(content_types=['text'])
def func(message):

    if (message.text == "Анекдоты"):
        btn1 = types.KeyboardButton("Травануть анекдотик")
        btn2 = types.KeyboardButton("Добавить анекдотик")
        btn_back = types.KeyboardButton("⬅️Назад")
        markup = types.ReplyKeyboardMarkup(
            resize_keyboard=True, row_width=2).add(btn1).add(btn2).add(btn_back)
        bot.send_message(
            message.chat.id, text="Отборные анекдоты", reply_markup=markup)

    elif (message.text == "Мемы"):
        btn1 = types.KeyboardButton("Получить смешнявку")
        btn2 = types.KeyboardButton("Добавить смешнявку")
        btn_back = types.KeyboardButton("⬅️Назад")
        markup = types.ReplyKeyboardMarkup(
            resize_keyboard=True, row_width=2).add(btn1).add(btn2).add(btn_back)
        bot.send_message(
            message.chat.id, text="Тупорылые мемасики", reply_markup=markup)

    elif (message.text == "⬅️Назад"):
        btn1 = types.KeyboardButton("Анекдоты")
        btn2 = types.KeyboardButton("Мемы")
        markup = types.ReplyKeyboardMarkup(
            resize_keyboard=True, row_width=2).add(btn1).add(btn2)
        bot.send_message(
            message.chat.id, text="Че ты в меню, выбирай и прикалывайся", reply_markup=markup)

    elif (message.text == "Травануть анекдотик"):
        bot.send_message(message.chat.id, text=BotDB.get_record())

    elif (message.text == "Добавить анекдотик"):
        send = bot.send_message(
            message.chat.id, text="Напиши свой юморной анекдот")
        bot.register_next_step_handler(send, add_db)

    elif (message.text == "Получить смешнявку"):
        file_path_type = ["./source/memes/*.*"]
        images = glob.glob(random.choice(file_path_type))
        random_image = random.choice(images)
        img = Image.open(random_image)

        # Like, dislike buttons
        markup = types.InlineKeyboardMarkup(row_width=2)
        btn_like = types.InlineKeyboardButton('👍🏽', callback_data='like')
        btn_dislike = types.InlineKeyboardButton('👎🏽', callback_data='dislike')
        btn_share = types.InlineKeyboardButton(
            'Поделиться с корешом🔄', callback_data='share')
        markup.add(btn_like, btn_dislike, btn_share)
        bot.send_photo(message.chat.id, img, reply_markup=markup)

    elif (message.text == "Добавить смешнявку"):
        send = bot.send_message(
            message.chat.id, text="Отправь свою юморную картинку")
        bot.register_next_step_handler(send, add_photo)

    else:
        bot.send_message(
            message.chat.id, text="Я тебя не понимаю 😓")


def add_db(message):
    if (message.text in name_of_buttons):
        bot.send_message(
            message.chat.id, text="Такие анекдотики мы уже знаем :(")
    else:
        BotDB.add_record(message.from_user.id, message.text)
        bot.reply_to(message, "Анекдот добавлен!")


def add_photo(message):
    try:
        file_info = bot.get_file(message.photo[-1].file_id)
        file_name, file_extention = os.path.splitext(file_info.file_path)
        downloaded_file_photo = bot.download_file(file_info.file_path)
        src = "./source/memes/" + message.chat.first_name + \
            "___" + message.photo[-1].file_id + file_extention
        with open(src, 'wb') as new_file:
            new_file.write(downloaded_file_photo)
        bot.send_message(
            message.chat.id, text="Ваш прикольчик добавлен !")

        sti = open('./source/bot_stuff/sb_sticker.webp', 'rb')
        bot.send_sticker(message.chat.id, sticker=sti)

    except Exception:
        bot.send_message(
            message.chat.id, text="Что-то пошло не так, попробуйте отправить фото заново!")


def share_to_friend(message):
    bot.send_message(message.chat.id,
                     text="Я потенциально крутая кнопка, но пока не работаю")


def dislike_foo(message):
    if (message.text in name_of_buttons):
        bot.send_message(
            message.chat.id, text="Тыкать по кнопкам - это не отзыв, друг)")
    else:
        bot.send_message(token_file.ADMIN_ID, message.text)


@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    if call.message:
        if call.data == 'like':
            bot.send_message(
                call.message.chat.id, text="Я знаю что прикол крутой, можешь в следующий раз не оценивать")
        elif call.data == 'dislike':
            send = bot.send_message(call.message.chat.id,
                                    text="Расскажи, что тебе не понравилось и мы попроубем это исправить 😢")
            bot.register_next_step_handler(send, dislike_foo)
        elif call.data == 'share':
            send = bot.send_message(
                call.message.chat.id, text="Перешлите сообщение с другом, которому вы хотите отправить прикол.\nМы не читаем эти сообщения!🤧")
            bot.register_next_step_handler(send, share_to_friend)


bot.polling(none_stop=True)
