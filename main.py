from datetime import datetime
import sqlite3

import telebot
from telebot import types

from hotels_api import search_cities, search_hotels
from credential import TELEGRAM_TOKEN
from settings import (
    HOTELS_COUNT_LIMIT,
    HOTEL_PHOTO_COUNT_LIMIT,
)

bot = telebot.TeleBot(TELEGRAM_TOKEN, parse_mode=None)


@bot.message_handler(commands=['hello-world'])
def hello_handler(message):
    bot.send_message(message.from_user.id, 'Привет')


@bot.message_handler(commands=['help'])
def help_handler(message):
    msg = [
        '/lowprice - топ самых дешёвых отелей в городе',
        '/highprice - топ самых дорогих отелей в городе',
        '/bestdeal -  топ отелей, наиболее подходящих по цене и расположению от центра',
        '/history - история поиска отелей',
    ]
    bot.send_message(message.from_user.id, '\n'.join(msg))


@bot.message_handler(commands=['lowprice', 'highprice', 'bestdeal'])
def get_city(message):
    bot.send_message(message.from_user.id, 'Введите название города')
    if message.text == '/lowprice':
        data = {'order': 'low'}
    elif message.text == '/highprice':
        data = {'order': 'high'}
    elif message.text == '/bestdeal':
        data = {'order': 'center'}
    bot.register_next_step_handler(message, check_city, data)


def check_city(message, data=None):
    cities = search_cities(message.text)
    if data['order'] == 'low':
        order = 0
    elif data['order'] == 'high':
        order = 1
    elif data['order'] == 'center':
        order = 2
    if cities:
        markup = types.InlineKeyboardMarkup(row_width=1)
        for city in cities:
            call_message = '{}.{}'.format(
                city['id'],
                order,
            )
            markup.add(types.InlineKeyboardButton(text=city['name'],
                                                  callback_data=call_message))
        bot.send_message(message.from_user.id, 'Выберите город',
                         reply_markup=markup)
    else:
        bot.send_message(message.from_user.id, 'Не найдено ни одного города')
        get_city(message)


@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    city_id, order = call.data.split('.')
    data = {'city': city_id}
    if order == '0':
        data['order'] = 'low'
    elif order == '1':
        data['order'] = 'high'
    elif order == '2':
        data['order'] = 'center'
    get_calendar(call.message, data)


def get_calendar(message, data):
    bot.send_message(message.chat.id, 'Укажите даты прибытия и выезда в формате\nДД.ММ.ГГГГ-ДД.ММ.ГГГГ')
    bot.register_next_step_handler(message, get_hotels_count, data)


def check_date_format(date):
    if date.count('.') != 2:
        return None
    if date.replace('.', '').isdigit():
        day, month, year = map(int, date.split('.'))
        try:
            date = datetime(day=day, month=month, year=year)
        except ValueError:
            return None
    if date < datetime.today():
        return None
    return date


def get_hotels_count(message, data):
    dates = message.text.replace(' ', '')
    if '-' in dates:
        date_begin, date_end = map(check_date_format, dates.split('-'))
        if date_begin and date_end and (date_begin < date_end):
            good_dates = True
        else:
            good_dates = False
    else:
        good_dates = False
    if good_dates:
        data['date_begin'] = date_begin
        data['date_end'] = date_end
        bot.send_message(message.from_user.id, 'Сколько отелей показать?')
        bot.register_next_step_handler(message, need_photo, data)
    else:
        bot.send_message(message.from_user.id, 'Даты введены неверно!')
        get_calendar(message, data)


def need_photo(message, data):
    if message.text.isdigit() and int(message.text) > 0:
        data['hotels_count'] = min(int(message.text), HOTELS_COUNT_LIMIT)
        bot.send_message(message.from_user.id,
                         'Показывать фото отелей (Да/Нет)?')
        bot.register_next_step_handler(message, get_hotel_photo_count, data)
    else:
        bot.send_message(message.from_user.id, 'Введите положительное число!')
        get_hotels_count(message, data)


def get_hotel_photo_count(message, data):
    if message.text.strip().lower() == 'да':
        bot.send_message(message.from_user.id,
                         'Сколько фото для каждого отеля показать?')
        bot.register_next_step_handler(message, check_hotel_photo_count, data)
    else:
        data['hotel_photo_count'] = 0
        get_hotels(message, data)


def check_hotel_photo_count(message, data):
    if message.text.isdigit() and int(message.text) >= 0:
        data['hotel_photo_count'] = min(int(message.text), HOTEL_PHOTO_COUNT_LIMIT)
        get_hotels(message, data)
    else:
        bot.send_message(message.from_user.id, 'Введите положительное число!')
        message.text = 'да'
        get_hotel_photo_count(message, data)


def get_hotels(message, data):
    hotels = search_hotels(
        data['city'],
        data['hotels_count'],
        data['hotel_photo_count'],
        data['date_begin'],
        data['date_end'],
        data['order'],
    )
    hotels_log = []
    for hotel in hotels:
        msg = '{0}\n{2}\n{3}\n{1}'.format(
            hotel['name'],
            hotel['price'],
            hotel['address'],
            hotel['center_dest'],
        )
        hotels_log.append(hotel['name'])
        photos = []
        for idx, photo in enumerate(hotel['photos']):
            if idx == 0:
                photos.append(types.InputMediaPhoto(media=photo, caption=msg))
            else:
                photos.append(types.InputMediaPhoto(media=photo))
        if photos:
            bot.send_media_group(message.chat.id, media=photos)
        else:
            bot.send_message(message.chat.id, msg)
    log(message, data, hotels_log)


def log(message, data, hotels):
    if data['order'] == 'low':
        command = '/lowprice'
    elif data['order'] == 'high':
        command = '/highprice'
    elif data['order'] == 'center':
        command = '/bestdeal'
    hotels = '; '.join(hotels)
    connection = sqlite3.connect('data.db')
    with connection:
        query = 'INSERT INTO HISTORY (chat_id, command, hotels) VALUES ({}, "{}", "{}")'.format(
            message.chat.id, command, hotels)
        connection.execute(query)


@bot.message_handler(commands=['history'])
def history_handler(message):
    connection = sqlite3.connect('data.db')
    with connection:
        query = 'SELECT command, datetime(timestamp, "localtime"), hotels FROM HISTORY WHERE chat_id={}'.format(
            message.chat.id)
        cursor = connection.cursor()
        cursor.execute(query)
        rows = cursor.fetchall()
    msg = '\n'.join(['{} {} {}'.format(*row) for row in rows])
    bot.send_message(message.from_user.id, msg)


bot.infinity_polling()
