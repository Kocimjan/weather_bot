import sqlite3
import time
from datetime import datetime, timedelta
from telebot import types
from bot import bot
import requests
import threading
import config

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
    if message.content_type == 'location':
        lat = message.location.latitude
        lon = message.location.longitude
        try:
            db.execute("UPDATE user SET lat = ?, lon = ? WHERE user_id = ?", lat, lon, user_id)
            db.commit()
            bot.send_message(chat_id, "Ваша локация успешно обновлено.")
        except Exception as e:
            bot.send_message(chat_id, f"Ошибка при сохранении ваших координат попробуйте позже или сообщите мне @TB4TE")
        finally:
            db.close()
    elif message.content_type == 'text':
        city = message.text
        try:
            db.execute("UPDATE user SET city = ?", city)
            db.commit()
            bot.send_message(chat_id, "Ваша локация успешно обновлено.")
        except:
            bot.send_message(chat_id, f"Ошибка при сохранении ваших координат попробуйте позже или сообщите мне @TB4TE")
        finally:
            db.close()


def set_location_next(message):
    db = database()
    user_id = message.from_user.id
    chat_id = message.chat.id
    if message.content_type == 'location':
        lat = message.location.latitude
        lon = message.location.longitude
        url = f'http://api.openweathermap.org/geo/1.0/reverse?lat={lat}&lon={lon}&appid={config.api_key}'
        convert_response = requests.get(url)
        data = convert_response.json()[0]
        city = data['local_names']['ru']
        try:
            username = message.from_user.username
            db.execute("INSERT or REPLACE INTO user (username, tg_id, city, lat, lon) VALUES (?, ?, ?, ?, ?)", username, user_id, city, lat, lon)
            bot.send_message(chat_id, "Ваша локация успешно установлена.")
        except:
            db.execute("INSERT OR REPLACE INTO user (tgid, lat, lon) VALUES (?, ?, ?)", user_id, lat, lon)
            bot.send_message(chat_id, "Ваша локация успешно установлена.")
        finally:
            db.commit()
            db.close()
    elif message.content_type == 'text':
        city = message.text
        try:
            username = message.from_user.username
            db.execute("INSERT OR REPLACE INTO user (username, tg_id, city) VALUES (?, ?, ?)", username, user_id, city)
            bot.send_message(chat_id, "Ваша локация успешно установлена.")
        except Exception as e:
            db.execute("INSERT OR REPLACE INTO user (username, tg_id, city) VALUES (?, ?)",  user_id, city)
            bot.send_message(chat_id, "Ваша локация успешно установлена.")
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


def user_exist(message):
    db = database()
    user_id = message.from_user.id
    user = db.execute("SELECT * FROM user WHERE tg_id = ?", user_id)
    db.close()
    if user:
        return True
    else:
        return False

def set_notification_frequency(message):
    chat_id = message.chat.id
    try:
        frequency = int(message.text)
        if frequency <= 0:
            raise ValueError
        bot.send_message(chat_id, "Теперь укажите время для каждой отправки уведомления (в формате ЧЧ:ММ), через запятую:")
        bot.register_next_step_handler(message, set_notification_times, frequency)
    except ValueError:
        bot.send_message(chat_id, "Пожалуйста, введите целое положительное число.")
        bot.register_next_step_handler(message, set_notification_frequency)


def set_notification_times(message, frequency):
    chat_id = message.chat.id
    user_id = message.from_user.id
    db = database()
    times_str = message.text.split(',')
    city = db.execute("SELECT city FROM user WHERE tg_id = ?", user_id)[0]
    try:
        times = []
        for time_str in times_str:
            hours, minutes = map(int, time_str.split(':'))
            if hours < 0 or hours > 23 or minutes < 0 or minutes > 59:
                raise ValueError
            times.append(time_str)
        times_str = ','.join(times)
        db.execute("INSERT OR REPLACE INTO user_notifications (chat_id, frequency, times, city) VALUES (?, ?, ?, ?)", chat_id, frequency, times_str, city[0])
        db.commit()
        db.close()
        bot.send_message(chat_id, "Уведомления успешно настроены!")
    except ValueError:
        bot.send_message(chat_id, "Пожалуйста, введите время в правильном формате (ЧЧ:ММ) и убедитесь, что оно корректно.")
        bot.register_next_step_handler(message, set_notification_times, frequency)

# Функция для выполнения планирования уведомлений
def schedule_notifications():
    db = database()
    while True:
        current_time = datetime.now()
        current_time += timedelta(hours=5)
        rows = db.execute("SELECT chat_id, times, city FROM user_notifications")
        if rows:
            print(current_time.strftime('%H:%M'))
            for row in rows:
                chat_id = row[0]
                times = row[1].split(',')
                city = row[2]
                if current_time.strftime('%H:%M') in times:
                    bot.send_message(chat_id, get_weather(config.api_key, city=city))
        time.sleep(60)  # Проверка каждую минуту

# Запуск потока для выполнения планирования уведомлений в фоне
thread = threading.Thread(target=schedule_notifications)
thread.start()