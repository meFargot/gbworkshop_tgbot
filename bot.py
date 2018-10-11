import random

import telebot
import requests
from telebot.types import Message

TOKEN = ""  # <<<--- ВСТАВИТЬ ТОКЕН
BASE_URL = "https://api.telegram.org/bot{}/".format(TOKEN)

stickers_to_set = []
sticker_flag = False  # Флаг создания набора стикеров

bot = telebot.TeleBot(TOKEN)

def generate_stickers(m:Message):
    """ Генерируем новый набор стикеров и отправляем в чат
        НЕ РАБОТАЕТ
    """
    global stickers_to_set
    payload = {
        'user_id': m.from_user.id,
        'name': "stkset_by_sergeyrobot",
        'title': 'Набор стикеров от Robot Sergey',
        'png_sticker': get_sticker_png(stickers_to_set[0].file_id,
                                       m.from_user.id),
        'emojis': stickers_to_set[0].emoji
    }
    r = requests.post(f'{BASE_URL}createNewStickerSet', data=payload)
    print(r.json())
    for stk in stickers_to_set[1:]:
        payload = {
            'user_id': m.from_user.id,
            'name': "stkset_by_sergeyrobot",
            'png_sticker': get_sticker_png(stk.file_id,
                                           m.from_user.id),
            'emojis': stk.emoji
        }
        r = requests.post(f'{BASE_URL}addStickerToSet', data=payload)
        print(r.json())


def get_sticker_png(file_id, user_id):
    """ Получаем стикер в png
        НЕ РАБОТАЕТ ПРАВИЛЬНО
    """
    file_info = bot.get_file(file_id)
    sticker_file = requests.get('https://api.telegram.org/file/bot{0}/{1}'.
                                format(TOKEN, file_info.file_path))
    payload = {
        'user_id': user_id,
        'png_sticker': sticker_file
    }
    file = requests.post(f'{BASE_URL}uploadStickerFile', data=payload)
    return file

@bot.message_handler(commands=['start'])
def send_welcome(message:Message):
    anekdot = """
    Царь позвал к себе Иванушку-дурака и говорит:
    – Если завтра не принесешь двух говорящих птиц – голову срублю.
    Иван принес филина и воробья. Царь говорит:
    – Ну, пусть что-нибудь скажут.
    Иван спрашивает:
    – Воробей, почем раньше водка в магазине была?
    Воробей:
    – Чирик.
    Иван филину:
    – А ты, филин, подтверди.
    Филин:
    – Подтверждаю.
    """
    bot.send_message(message.chat.id, anekdot)


@bot.message_handler(commands=['create', 'stop'])
def send_welcome(message:Message):
    """ Обрабатываем команды для создания архива со стикерами
        create - все стикеры присланные после этой команды пойдут в архив
        stop - после этой команды возвращаем набор стикеров
    """
    global sticker_flag
    global stickers_to_set
    if message.text == '/create':
        sticker_flag = True
        bot.send_message(message.chat.id, 'Отправляй мне стикеры, потом /stop')
    if message.text == '/stop':
        if len(stickers_to_set) > 0:
            generate_stickers(message)
            sticker_flag = False
            stickers_to_set = []
        else:
            bot.send_message(message.chat.id, 'Сначала отправь /start и несколько стикеров')


@bot.message_handler(func=lambda message: message.content_type == "text" and
                                          'подтверди' in message.text.lower())
def confirm_or_not(message:Message):
    """ Если в сообщении есть слово "подтверди", то отвечаем одним из заранее
        приготовленных ответов
    """
    confirms = [
        'Так точно',
        'Угу',
        'Подтверждаю',
        'Именно так',
        'Бесспорно',
        'Именно',
        'Нет',
        'Это не так',
        'Точно нет'
    ]
    bot.send_message(message.chat.id, random.choice(confirms))


@bot.message_handler(content_types=["text"])
def say_ugu_or_answer(message:Message):
    """ Отвечаем на остальные сообщения в 50% "Угу", а в остальных 50%
        случаях проверяем: если в сообщении есть вопрос, то отвечаем на него
        заранее приготовленными фразами
    """
    answers = [
        'А сам то как думаешь?',
        'Спроси меня еще раз',
        'Подумаю над этим вопросом',
    ]
    if random.random() > 0.5:
        bot.send_message(message.chat.id, 'Угу')
    elif "?" in message.text:
        bot.send_message(message.chat.id, random.choice(answers))

#message.content_type == "sticker"
@bot.message_handler(content_types=["sticker"])
def return_sticker_png(message:Message):
    """ Если не собираем набор стикеров, то возвращаем стикер в виде картинки.
        Иначе добавляем стикеры в список
    """
    global sticker_flag
    if sticker_flag == False:
        file_info = bot.get_file(message.sticker.file_id)
        sticker_file = requests.get('https://api.telegram.org/file/bot{0}/{1}'.
                                    format(TOKEN, file_info.file_path))
        bot.send_photo(message.chat.id, sticker_file.content)
    else:
        stickers_to_set.append(message.sticker)
        bot.send_message(message.chat.id, 'Добавлено стикеров: {}'.format(len(stickers_to_set)))


bot.polling()
