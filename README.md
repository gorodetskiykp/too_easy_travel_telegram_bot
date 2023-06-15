# too_easy_travel_telegram_bot
Too Easy Travel Telegram Bot


rapidapi.com

Для работы скрипта нужен файл credential в корневом каталоге с тремя константами:
- TELEGRAM_TOKEN = строка - telegram-токен бота
- X_RapidAPI_Key = строка - токен авторизации с сайта rapidapi.com (hotels4)
- X_RapidAPI_Host = 'hotels4.p.rapidapi.com'


Перед запуском бота нужно создать БД - выполнить init_db.py


1. Зарегистрироваться на сайте rapidapi.com.
2. Перейти в API Marketplace → категория Travel → Hotels (либо просто перейти по прямой ссылке на документацию Hotels API Documentation).
3. Нажать кнопку Subscribe to Test.
4. Выбрать бесплатный пакет (Basic).


У базового пакета есть ограничение по количеству запросов в месяц, а именно — 500


1. Узнать топ самых дешёвых отелей в городе (команда /lowprice).
2. Узнать топ самых дорогих отелей в городе (команда /highprice).
3. Узнать топ отелей, наиболее подходящих по цене и расположению от центра (самые дешёвые и находятся ближе всего к центру) (команда /bestdeal).
4. Узнать историю поиска отелей (команда /history)


t.me/TooEasyTravelTelegramBot
