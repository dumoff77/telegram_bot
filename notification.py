#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = "dmitry sirenchenko"
__copyright__ = "Copyright 2019, bachelor diploma work"
__email__ = "sirenchenkod@gmail.com"

from datetime import datetime, timedelta

import telebot
from pymongo import MongoClient, errors

from token import TOKEN


class VacancyNotifier:
    def __init__(self):
        print 'init'
        token = TOKEN
        self.bot = telebot.TeleBot(token)
        client = MongoClient('localhost', 27017)
        self.db = client['telegram_bot']

    def notify_users(self):
        cursor = self.db.users.find({})
        yesterday_time = datetime.now() + timedelta(hours=-25)
        for user_data in cursor:
            list_vacancies = self.db.vacancy.find({"location": {"$in": user_data['locations']},
                                                   "Specialization": {"$in": user_data['vacancies']},
                                                  "date": {"$gt": yesterday_time}})
            for vacancy_link in list_vacancies:
                self.bot.send_message(user_data['_id'], vacancy_link['_id'])


def main():
    vn = VacancyNotifier()
    vn.notify_users()


if __name__ == '__main__':
    main()