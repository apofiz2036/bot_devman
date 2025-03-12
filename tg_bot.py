import requests
import os
from telegram import Bot
from dotenv import load_dotenv
from pprint import pprint
from time import sleep
import logging
from logging.handlers import RotatingFileHandler


class TelegramLogsHandler(logging.Handler):
    def __init__(self, tg_bot, chat_id):
        super().__init__()
        self.chat_id = chat_id
        self.tg_bot = tg_bot

    def emit(self, record):
        log_entry = self.format(record)
        self.tg_bot.send_message(chat_id=self.chat_id, text=log_entry)


def main():
    load_dotenv()
    DEVMAN_TOKEN = os.environ['DEVMAN_TOKEN']
    TELEGRAM_BOT_TOKEN = os.environ['TELEGRAM_TOKEN']
    CHAT_ID = os.environ['CHAT_ID']
    bot = Bot(token=TELEGRAM_BOT_TOKEN)

    logger = logging.getLogger(__name__)
    logger.setLevel(logging.WARNING)

    rotating_handler = RotatingFileHandler(
        'app.log',
        maxBytes=20000,
        backupCount=2
    )
    rotating_handler.setFormatter(logging.Formatter("%(process)d %(levelname)s %(message)s"))
    logger.addHandler(rotating_handler)

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(logging.Formatter("%(process)d %(levelname)s %(message)s"))
    logger.addHandler(stream_handler)

    telegram_handler = TelegramLogsHandler(bot, CHAT_ID)
    telegram_handler.setFormatter(logging.Formatter("%(process)d %(levelname)s %(message)s"))
    logger.addHandler(telegram_handler)

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
            logger.error("Нет ответа от сервера")
        except requests.exceptions.ConnectionError:
            logger.error("Отрубился интернет")
            sleep(60)
        except Exception as e:
            logger.exception(f'Произошла ошибка: {e}')
            break


if __name__ == '__main__':
    main()
