import requests
import os
from telegram import Bot
from dotenv import load_dotenv
from pprint import pprint
from time import sleep


def main():
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
            response = requests.get(url, headers=headers, params=params, timeout=60)
            response.raise_for_status()

            devman_response = response.json()
            pprint(devman_response)

            if devman_response['status'] == 'found':
                timestamp = devman_response['last_attempt_timestamp']
            elif devman_response['status'] == 'timeout':
                timestamp = devman_response['timestamp_to_request']

            if devman_response['new_attempts'][0]['is_negative']:
                lesson_title = devman_response['new_attempts'][0]['lesson_title']
                lesson_url = devman_response['new_attempts'][0]['lesson_url']
                text = f'Проверена работа "{lesson_title}", ну блин, есть ошибки. .\n \n Ссылка на урок: {lesson_url}'
                bot.send_message(chat_id=CHAT_ID, text=text)
            else:
                lesson_title = devman_response['new_attempts'][0]['lesson_title']
                lesson_url = devman_response['new_attempts'][0]['lesson_url']
                text = f'Проверена работа "{lesson_title}", УРА! ПРИНЯТО!. .\n \n Ссылка на урок: {lesson_url}'
                bot.send_message(chat_id=CHAT_ID, text=text)
        except requests.exceptions.ReadTimeout:
            continue
        except requests.exceptions.Timeout:
            print('Нет ответа от сервера')
        except requests.exceptions.ConnectionError:
            print('Отрубился интернет')
            sleep(60)


if __name__ == '__main__':
    main()
