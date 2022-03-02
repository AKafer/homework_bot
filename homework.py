import os
import time
import telegram
import requests
from dotenv import load_dotenv
import datetime as DT  

load_dotenv()


PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')


RETRY_TIME = 5
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}


HOMEWORK_STATUSES = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}


def send_message(bot, message):
    bot.send_message(TELEGRAM_CHAT_ID, message)


def get_api_answer(current_timestamp):
    timestamp = current_timestamp
    params = {'from_date': int(timestamp)}
    response = requests.get(ENDPOINT, headers=HEADERS, params=params, verify=False)
    return response


def check_response(response):
    print(response.json().get('homeworks'))
    return response.json().get('homeworks')


def parse_status(homework):
    homework_name = homework.get('homework_name')
    homework_status = homework.get('status')

    ...

    verdict = HOMEWORK_STATUSES.get(homework_status)

    ...

    return f'Изменился статус проверки работы "{homework_name}". {verdict}'

"""
def check_tokens():

"""    


def main():
    """Основная логика работы бота."""

    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    response = get_api_answer(0)
    print(response.json().get('homeworks')[0].get('status'))
    homeworks = check_response(response)
    if homeworks:
        message = parse_status(homeworks[0])
        print(message)
        send_message(bot, message)
    current_timestamp = int(time.time())

    while True:
        try:
            response = get_api_answer(current_timestamp)
            if check_response(response):
                print("есть")
            else:
                print("пусто")
            

            ...

            current_timestamp = int(time.time())
            time.sleep(RETRY_TIME)

        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            ...
            time.sleep(RETRY_TIME)
        else:
            ...


if __name__ == '__main__':
    main()

