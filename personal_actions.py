from bot import bot
from telebot import types
import functions
from config import api_key


@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, """Привет! Я - ваш надежный погодный помощник! Хотите всегда быть в курсе текущей погоды в любом 
уголке мира? Тогда доверьтесь мне!

🌤️ Просто отправьте мне название вашего города или поделитесь своей геолокацией, и я предоставлю вам актуальную информацию о температуре, облачности, влажности и скорости ветра.

📡 Также, чтобы всегда быть в курсе изменений погоды, вы можете подписаться на рассылку актуальной погоды с помощью команды /subscribe.

🔄 Если вы хотите обновить своё местоположение или добавить новое, воспользуйтесь командами /update_location и /set_location соответственно.

Не позволяйте погоде влиять на ваши планы! Доверьтесь мне и будьте в курсе всех изменений!

👨‍💻 Этот бот разработан @TBATE. Если у вас есть какие-либо вопросы или предложения, не стесняйтесь обращаться!""")


# Обработчик команды /get_location
@bot.message_handler(commands=['update_location'])
def update_location(message):
    # Создание клавиатуры с кнопкой "Поделиться местоположением"
    keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    button = types.KeyboardButton(text="Отправить местоположение", request_location=True)
    keyboard.add(button)

    # Отправка сообщения с запросом местоположения и клавиатурой
    bot.send_message(message.chat.id, "Поделись своим местоположением, нажав на кнопку ниже:", reply_markup=keyboard)


@bot.message_handler(commands=['set_location'])
def set_location(message):
    # Создание клавиатуры с кнопкой "Поделиться местоположением"
    keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    button = types.KeyboardButton(text="Отправить местоположение", request_location=True)
    keyboard.add(button)

    # Отправка сообщения с запросом местоположения и клавиатурой
    bot.send_message(message.chat.id, "Поделись своим местоположением, нажав на кнопку ниже:", reply_markup=keyboard)
    bot.register_next_step_handler(message, functions.set_location_next)


@bot.message_handler(commands=['subscribe'])
def subscribe(message):
    db = functions.database()
    chat_id = message.chat.id
    user_id = message.from_user.id
    check = db.execute("SELECT user_id FROM subscribe WHERE user_id = ?", user_id)
    if not check:
        db.execute("INSERT INTO subscribe (user_id, chat_id) VALUES ((SELECT user_id FROM user WHERE tg_id = ?), ?", chat_id, chat_id)
        db.commit()
    db.close()


# Обработчик для сообщений с типом "location"
@bot.message_handler(content_types=['location'])
def handle_location(message):
    chat_id = message.chat.id
    lat = message.location.latitude
    lon = message.location.longitude
    bot.send_message(chat_id, functions.get_weather(api_key, lat=lat, lon=lon))
