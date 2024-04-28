from bot import bot
from telebot import types
import functions
from config import api_key


@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, """Привет! Я - ваш надежный погодный помощник! Хотите всегда быть в курсе текущей погоды в любом 
уголке мира? Тогда доверьтесь мне!

🌤️ Просто отправьте мне название вашего города или поделитесь своей геолокацией, и я предоставлю вам актуальную информацию о погоде.

📡 Также, чтобы всегда быть в курсе изменений погоды, вы можете подписаться на рассылку актуальной погоды с помощью команды /set_notification.

🔄 Если вы хотите обновить своё местоположение или добавить новое, воспользуйтесь командами /update_location и /set_location соответственно.

Не позволяйте погоде влиять на ваши планы! Доверьтесь мне и будьте в курсе всех изменений!

👨‍💻 Этот бот разработан @TBATE. Если у вас есть какие-либо вопросы или предложения, не стесняйтесь обращаться!""")
    
    if not functions.user_exist(message):
        set_location(message)


@bot.message_handler(commands=['update_location'])
def update_location(message):
    keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    button = types.KeyboardButton(text="Отправить местоположение", request_location=True)
    keyboard.add(button)

    bot.send_message(message.chat.id, "Отправь названия города или, поделись своим местоположением, нажав на кнопку ниже:",
                     reply_markup=keyboard)
    bot.register_next_step_handler(message, functions.update_location_next)

# Обработчик команды для настройки локации
@bot.message_handler(commands=['set_location'])
def set_location(message):
    keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    button = types.KeyboardButton(text="Отправить местоположение", request_location=True)
    keyboard.add(button)

    bot.send_message(message.chat.id, "Отправь названия города, или поделись своим местоположением, нажав на кнопку ниже:", reply_markup=keyboard)
    bot.register_next_step_handler(message, functions.set_location_next)


# Обработчик команды для настройки уведомлений
@bot.message_handler(commands=['set_notification'])
def set_notification(message):
    chat_id = message.chat.id
    bot.send_message(chat_id, "Сколько раз в день вы хотели бы получать уведомления?")
    bot.register_next_step_handler(message, functions.set_notification_frequency)



# Обработчик для сообщений с типом "location, text"
@bot.message_handler(content_types=['location', 'text'])
def handle_location(message):
    chat_id = message.chat.id
    if message.content_type == 'location':
        lat = message.location.latitude
        lon = message.location.longitude
        bot.send_message(chat_id, functions.get_weather(api_key, lat=lat, lon=lon))
    elif message.content_type == 'text':
        bot.send_message(chat_id, functions.get_weather(api_key, city=message.text))



