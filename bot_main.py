#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = "dmitry sirenchenko"
__copyright__ = "Copyright 2019, bachelor diploma work"
__email__ = "sirenchenkod@gmail.com"

from datetime import datetime
import re

import telebot
from pymongo import MongoClient, errors

from token import TOKEN


token = TOKEN
bot = telebot.TeleBot(token)
client = MongoClient('localhost', 27017)
db = client['telegram_bot']
cursor = db.config.find({"_id": "Specialization"}, {"_id": False})
arr_specialization = list(cursor)[0].values()[0]
list_of_commands = ['/' + i for i in arr_specialization]


@bot.message_handler(func=lambda message: True,
                     content_types=['audio', 'video', 'document', 'location', 'contact', 'sticker'])
def error_command(message):
    bot.send_message(message.from_user.id, "Error, please use /help command to see available methods")


@bot.message_handler(commands=arr_specialization)
def vacancy_click(message):
    save_chat_history(message)
    msg = message.json['text'].replace('/', '')
    keyboard = telebot.types.InlineKeyboardMarkup()  # клавиатура
    key_3 = telebot.types.InlineKeyboardButton(text='3', callback_data='3')
    keyboard.add(key_3)  # добавляем кнопку "3" в клавиатуру
    key_7 = telebot.types.InlineKeyboardButton(text='7', callback_data='7')
    keyboard.add(key_7)
    key_15 = telebot.types.InlineKeyboardButton(text='15', callback_data='15')
    keyboard.add(key_15)
    question = 'How many vacancies you want to see? {}'.format(msg)
    bot.send_message(message.from_user.id, text=question, reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: True)
def callback_worker(call):
    callback_message =  call.message.json['text']
    selected_specialis = callback_message.split('? ')[-1]
    cursor = db.vacancy.find({"Specialization": selected_specialis}).limit(int(call.data))
    for vacancy in cursor:
        locations_with_hashtag = ['#' + i for i in vacancy['location']]
        speciality_with_hashtag = '#' + selected_specialis
        vacancy_locations = (', '.join(locations_with_hashtag))
        bot.send_message(call.message.chat.id,
                         vacancy['_id']+' '+speciality_with_hashtag+' '+vacancy_locations)
    question = r'Can I help you with something else? /show /help /{}'.format(selected_specialis)
    bot.send_message(call.message.chat.id, question)


@bot.message_handler(commands=['start'])
def send_welcome(message):
    save_chat_history(message)
    bot.send_message(message.from_user.id, 'Willkommen!')
    bot.send_message(message.from_user.id, 'Print /help to get list of available commands')


@bot.message_handler(commands=['help'])
def send_welcome(message):
    save_chat_history(message)
    bot.send_message(message.from_user.id, 'Use /show to get list of available speciality\n'
                                           'Use /reg_notification:<list of locations>:<list specialisations>'
                                           ' for vacancy automated notification.\n'
                                           'Use /remove to removing autonotification')


@bot.message_handler(commands=['show'])
def send_welcome(message):
    save_chat_history(message)
    response_list = ' ,'.join(list_of_commands)
    bot.send_message(message.from_user.id, 'Please, make a choiсe')
    bot.send_message(message.from_user.id, response_list)


@bot.message_handler(regexp=".+\?")
def handle_message(message):
    save_chat_history(message)
    bot.send_message(message.from_user.id, "Unfortunately I can not answer for your question =(")


@bot.message_handler(regexp=".+ello.*")
def handle_message(message):
    save_chat_history(message)
    reply = 'Hi %s, i am created to help people search for vacancies, please print /help' % message.from_user.first_name
    bot.send_message(message.from_user.id, reply)


@bot.message_handler(regexp=".*reg.*noti*")
def handle_message(message):
    save_chat_history(message)
    try:
        m = re.search(r'reg.*noti.*:(.+):(.+)', message.json['text'])
        notify_data = {"date": datetime.now()}
        notify_data.update({"_id": message.json.get('from', {}).get('id', None)})
        notify_data.update({"username": message.json.get('from', {}).get('username', None)})
        notify_data.update({"first_name": message.json.get('from', {}).get('first_name', None)})
        notify_data.update({"last_name": message.json.get('from', {}).get('last_name', None)})
        notify_data.update({"text": message.json.get('text', None)})
        notify_data.update({"locations": m.group(1).split(',')})
        notify_data.update({"vacancies": m.group(2).split(',')})
        db.users.save(notify_data)
        bot.send_message(message.from_user.id, 'Registration for notifications successfully completed!')
    except Exception, why:
        print why, message.json['text']
        bot.send_message(message.from_user.id, 'Error. Please try again.')
        bot.send_message(message.from_user.id, 'Usage example: /reg_notification:Lviv,Киев,Kyiv,Київ:Python,Java')


@bot.message_handler(commands=['remove'])
def handle_message(message):
    save_chat_history(message)
    try:
        db.users.remove({"_id": message.json.get('from', {}).get('id', None)})
        bot.send_message(message.from_user.id, 'registration has been removed')
    except:
        bot.send_message(message.from_user.id, 'Error. Registration not removed')


@bot.message_handler(func=lambda message: True, content_types=['text'])
def default_command(message):
    save_chat_history(message)
    bot.send_message(message.from_user.id, "Error, please use command /help to show available commands")


def save_chat_history(message):
    history = {"date": datetime.now()}
    history.update({"chat_id": message.json.get('from', {}).get('id', None)})
    history.update({"username": message.json.get('from', {}).get('username', None)})
    history.update({"first_name": message.json.get('from', {}).get('first_name', None)})
    history.update({"last_name": message.json.get('from', {}).get('last_name', None)})
    history.update({"text": message.json.get('text', None)})
    db.history.insert(history)


def main_loop():
    bot.polling(True)


if __name__ == '__main__':
    try:
        main_loop()
    except KeyboardInterrupt:
        print('Exiting by user request.')
        exit(0)