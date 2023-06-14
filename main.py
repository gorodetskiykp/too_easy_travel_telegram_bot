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
    bot.send_message(message.from_user.id, 'help')


@bot.message_handler(commands=['lowprice'])
def lowprice_handler(message):
    bot.send_message(message.from_user.id, 'Введите название города')
    data = {}
    bot.register_next_step_handler(message, get_hotels_count, data)


@bot.message_handler()
def get_hotels_count(message, data):
    if not data:
        data['city'] = message.text
    bot.send_message(message.from_user.id, 'Сколько отелей показать?')
    bot.register_next_step_handler(message, need_photo, data)


@bot.message_handler()
def need_photo(message, data):
    if message.text.isdigit() and int(message.text) > 0:
        data['hotels_count'] = min(int(message.text), HOTELS_COUNT_LIMIT)
        bot.send_message(message.from_user.id,
                         'Показывать фото отелей (Да/Нет)?')
        bot.register_next_step_handler(message, get_hotel_photo_count, data)
    else:
        bot.send_message(message.from_user.id, 'Введите положительное число!')
        get_hotels_count(message, data)


@bot.message_handler()
def get_hotel_photo_count(message, data):
    if message.text.strip().lower() == 'да':
        bot.send_message(message.from_user.id,
                         'Сколько фото для каждого отеля показать?')
        bot.register_next_step_handler(message, check_hotel_photo_count, data)
    else:
        data['hotel_photo_count'] = 0
        send_hotels(message, data)


@bot.message_handler()
def check_hotel_photo_count(message, data):
    if message.text.isdigit() and int(message.text) >= 0:
        data['hotel_photo_count'] = min(int(message.text),
                                        HOTEL_PHOTO_COUNT_LIMIT)
        send_hotels(message, data)
    else:
        bot.send_message(message.from_user.id, 'Введите положительное число!')
        message.text = 'да'
        get_hotel_photo_count(message, data)


def send_hotels(message, data):
    cities = search_cities(data['city'])
    if cities:
        markup = types.InlineKeyboardMarkup(row_width=1)
        for city in cities:
            call_message = '{}.{}.{}'.format(
                data['hotels_count'],
                data['hotel_photo_count'],
                city['id'],
            )
            markup.add(types.InlineKeyboardButton(text=city['name'],
                                                  callback_data=call_message))
        bot.send_message(message.from_user.id, 'Выберите город',
                         reply_markup=markup)
    else:
        bot.send_message(message.from_user.id, 'Не найдено ни одного города')
        lowprice_handler(message)


@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    if call.message:
        print(call.data)
        hotels_count, hotel_photo_count, city_id = call.data.split('.')
        hotels = search_hotels(city_id, hotels_count, hotel_photo_count)
        for hotel in hotels:
            msg = '{0}\n{2}\n{3}\n{1}'.format(
                hotel['name'],
                hotel['price'],
                hotel['address'],
                hotel['center_dest'],
            )
            # bot.send_message(call.message.chat.id, msg)
            photos = []
            for idx, photo in enumerate(hotel['photos']):
                if idx == 0:
                    photos.append(types.InputMediaPhoto(media=photo, caption=msg))
                else:
                    photos.append(types.InputMediaPhoto(media=photo))
            bot.send_media_group(call.message.chat.id, media=photos)



@bot.message_handler(commands=['highprice'])
def highprice_handler(message):
    bot.send_message(message.from_user.id, 'highprice')


@bot.message_handler(commands=['bestdeal'])
def bestdeal_handler(message):
    bot.send_message(message.from_user.id, 'bestdeal')


@bot.message_handler(commands=['history'])
def history_handler(message):
    bot.send_message(message.from_user.id, 'history')



bot.infinity_polling()
