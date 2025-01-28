import requests
import os
from telegram import Bot
from dotenv import load_dotenv
from pprint import pprint

load_dotenv()
DEVMAN_TOKEN = os.environ['DEVMAN_TOKEN']
TELEGRAM_BOT_TOKEN = os.environ['TELEGRAM_TOKEN']
CHAT_ID = os.environ['CHAT_ID']

bot = Bot(token=TELEGRAM_BOT_TOKEN)

url = 'https://dvmn.org/api/long_polling/'
headers = {
    "Authorization": f'Token {DEVMAN_TOKEN}'
}

timestamp = None

while True:
    params = {}
    if timestamp:
        params['timestamp'] = timestamp

    try:
        response = requests.get(url, headers=headers, params=params, timeout=5)
        response.raise_for_status()

        data = response.json()
        pprint(data)

        if data['status'] == 'found':
            new_attempts = data['new_attempts']
            timestamp = data['last_attempt_timestamp']
        elif data['status'] == 'timeout':
            timestamp = data['timestamp_to_request']

        if data['new_attempts'][0]['is_negative'] == True:
            lesson_title = data['new_attempts'][0]['lesson_title']
            lesson_url = data['new_attempts'][0]['lesson_url']
            text = f'Проверена работа "{lesson_title}", ну блин, есть ошибки. .\n \n Ссылка на урок: {lesson_url}'
            bot.send_message(chat_id=CHAT_ID, text=text)
        else:
            lesson_title = data['new_attempts'][0]['lesson_title']
            lesson_url = data['new_attempts'][0]['lesson_url']
            text = f'Проверена работа "{lesson_title}", УРА! ПРИНЯТО!. .\n \n Ссылка на урок: {lesson_url}'
            bot.send_message(chat_id=CHAT_ID, text=text)
    except requests.exceptions.Timeout:
        print('Нет ответа')
    except requests.exceptions.ConnectionError:
        print('Отрубился интернет')
