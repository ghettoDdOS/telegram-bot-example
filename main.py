import os

import requests

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    CallbackQueryHandler,
    CommandHandler,
    Filters,
    MessageHandler,
    Updater,
)

OPEN_WEATHER_API = "https://api.openweathermap.org/"
OPEN_WEATHER_KEY = os.environ.get("OPEN_WEATHER_KEY")
TELEGRAM_API_KEY = os.environ.get("TELEGRAM_API_KEY")
assert OPEN_WEATHER_KEY, "Укажите ключ от API OpenWeather"
assert TELEGRAM_API_KEY, "Укажите ключ от API Telegram"


def start(update, context):
    keyboard = [
        [
            InlineKeyboardButton("Погода", callback_data="/weather"),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    user = update.effective_user
    update.message.reply_markdown_v2(
        rf"Привет {user.mention_markdown_v2()}\!", reply_markup=reply_markup
    )


def button(update, context):
    query = update.callback_query
    query.answer()

    if query.data == "/weather":
        query.edit_message_text(
            text="Что бы узнать погоду введите /weather {Город}",
        )


def get_city(city_name):
    res = requests.get(
        OPEN_WEATHER_API + "geo/1.0/direct",
        params={
            "q": city_name,
            "appid": OPEN_WEATHER_KEY,
        },
    )
    return res.json()


def get_weather(lat, lon):
    res = requests.get(
        OPEN_WEATHER_API + "data/2.5/weather",
        params={
            "lat": lat,
            "lon": lon,
            "appid": OPEN_WEATHER_KEY,
            "units": "metric",
            "lang": "ru",
        },
    )
    return res.json()


def send_weather(update, context):
    city_name = update.message.text.lstrip("/weather ")
    city = get_city(city_name)
    try:
        weather = get_weather(city[0]["lat"], city[0]["lon"])
    except KeyError:
        update.message.reply_text("Город не найден")
    except Exception:
        update.message.reply_text("Ошибка в работе бота")
    update.message.reply_text(
        f"{city_name}\nСегодня: {weather['weather'][0]['description']}\nТемпература: {weather['main']['temp']}\nОщущается как: {weather['main']['feels_like']}",
    )


def echo(update, context):
    update.message.reply_text(update.message.text)


def main():
    updater = Updater(TELEGRAM_API_KEY)

    dispatcher = updater.dispatcher
    dispatcher.add_handler(CommandHandler("start", start))
    updater.dispatcher.add_handler(CallbackQueryHandler(button))
    dispatcher.add_handler(CommandHandler("weather", send_weather))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, echo))
    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main()
