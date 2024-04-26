import sqlite3
from telebot import types
from bot import bot
import requests


class database:

    def __init__(self):
        self.db_name = "weather.db"
        self.conn = sqlite3.connect(self.db_name)
        self.sql = self.conn.cursor()

    def execute(self, query, *params):
        if params is None:
            self.sql.execute(query)
            data = self.sql.fetchall()
        else:
            self.sql.execute(query, params)
            data = self.sql.fetchall()
        if data:
            return data

    def commit(self):
        self.conn.commit()

    def close(self):
        self.conn.close()


def update_location_next(message):
    db = database()
    user_id = message.from_user.id
    chat_id = message.chat.id
    lat = message.location.latitude
    lon = message.location.longitude
    try:
        db.execute("UPDATE user SET lat=?, lon=? WHERE user_id=?", lat, lon, user_id)
        db.commit()
        bot.send_message(chat_id, "")
    except Exception as e:
        bot.send_message(chat_id, f"Ошибка при сохранении ваших координат: {e}")
    finally:
        db.close()


def set_location_next(message):
    db = database()
    user_id = message.from_user.id
    lat = message.location.latitude
    lon = message.location.longitude
    try:
        username = message.from_user.username
        db.execute("INSERT INTO user (username, tg_id, lat, lon) VALUES (?, ?, ?)", username, user_id, lat, lon)
    except:
        db.execute("INSERT INTO user (tgid, lat, lon) VALUES (?, ?, ?)", user_id, lat, lon)
    finally:
        db.commit()
        db.close()


def get_weather(api_key, city=None, lat=None, lon=None):
    if lat and lon:
        url = f'http://api.openweathermap.org/geo/1.0/reverse?lat={lat}&lon={lon}&appid={api_key}'
        convert_response = requests.get(url)
        data = convert_response.json()[0]
        city = data['local_names']['ru']
    if city:
        url = f'http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric&lang=ru'
    response_weather = requests.get(url)
    if response_weather.status_code == 200:
        weather_data = response_weather.json()
        wind_speed = weather_data['wind']['speed']
        temperature = weather_data['main']['temp']
        description = weather_data['weather'][0]['description']
        return f'Погода в городе {city}: {description}, Температура: {temperature}°C, Скорость ветра: {wind_speed} м/с'
    else:
        return 'Ошибка при получении данных о погоде', response_weather

