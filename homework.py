import os  # на ГтиХабе у меня лежит файл Procfile - не папка
import time  # знаю почему на Яндексе появляется папка
import requests  # на Heroku bot работает
import sys

import telegram
import logging
from dotenv import load_dotenv
from http import HTTPStatus

from exceptions import NotStatusOkException, NotTokenException

load_dotenv()

PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
RETRY_TIME = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}
# имя переменной задано Яндексом, сказано их не менять
HOMEWORK_STATUSES = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.',
}
ERROR_MEMORY = None


def send_message(bot, message):
    """Отправляет сообщение в Телеграм."""
    bot.send_message(TELEGRAM_CHAT_ID, message)
    logging.info('Отправлено сообщение в Телеграм')


def get_api_answer(current_timestamp):
    """Направляет запрос к API ЯндексПрактикума,возращает ответ."""
    params = {'from_date': current_timestamp}
    try:
        logging.info('Отправляю запрос к API ЯндексПрактикума')
        response = requests.get(
            ENDPOINT,
            headers=HEADERS,
            params=params,
        )
        if response.status_code != HTTPStatus.OK:
            logging.error('Недоступность эндпоинта')
            raise NotStatusOkException('Недоступность эндпоинта')
        return response.json()
    except ConnectionError:
        logging.error('Сбой при запросе к эндпоинту')
        raise ConnectionError('Сбой при запросе к эндпоинту')


def check_response(response):
    """Возвращает содержимое в ответе от ЯндексПрактикума."""
    if isinstance(response, list):  # без этой проверки не проходят тесты
        response = response[0]
        logging.info('API передал список')
    if not isinstance(response, dict):
        logging.error('API передал не словарь')
        raise TypeError('API передал не словарь')
    homework = response.get('homeworks')
    if homework is None:
        logging.error('API не содержит ключа homeworks')
        raise KeyError('API не содержит ключа homeworks')
    if not isinstance(homework, list):
        logging.error('Содержимое не список')
        raise TypeError('Содержимое не список')
    return homework


def parse_status(homework):
    """Извлекает статус работы из ответа ЯндексПракутикум."""
    homework_name = homework.get('homework_name')
    if homework_name is None:
        logging.error('В ответе API нет ключа homework_name')
        raise KeyError('В ответе API нет ключа homework_name')
    homework_status = homework.get('status')
    if homework_status is None:
        logging.error('В ответе API нет ключа homework_status')
        raise KeyError('В ответе API нет ключа homework_status')
    verdict = HOMEWORK_STATUSES.get(homework_status)
    if verdict is None:
        logging.error('Неизвестный статус')
        raise KeyError('Неизвестный статус')
    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def check_tokens():
    """Проверяет наличие токенов."""
    flag = all([
        PRACTICUM_TOKEN is not None,
        TELEGRAM_TOKEN is not None,
        TELEGRAM_CHAT_ID is not None
    ])
    return flag


def main():
    """Основная логика работы бота."""
    global ERROR_MEMORY
    logging.basicConfig(
        level=logging.INFO,
        format=(
            '%(asctime)s - [%(levelname)s][%(lineno)s][%(filename)s]'
            '[%(funcName)s]- %(message)s'
        ),
        handlers=[logging.StreamHandler(sys.stdout)]
    )
    if check_tokens():
        logging.info('Токены впорядке')
    else:
        logging.critical(
            'Не обнаружен один из ключей PRACTICUM_TOKEN,'
            'TELEGRAM_TOKEN, TELEGRAM_CHAT_ID'
        )
        raise NotTokenException(
            'Не обнаружен один из ключей PRACTICUM_TOKEN,'
            'TELEGRAM_TOKEN, TELEGRAM_CHAT_ID'
        )
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    current_timestamp = int(time.time())
    while True:
        try:
            response = get_api_answer(current_timestamp)
            homeworks = check_response(response)
            if homeworks:
                logging.info('Статус изменился!!!!!!!!!!!!')
                message = parse_status(homeworks[0])
                send_message(bot, message)
            else:
                logging.info('Статус не изменился')
            current_timestamp = int(time.time())
        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            logging.error(message)
            if str(error) != str(ERROR_MEMORY):
                ERROR_MEMORY = error
                send_message(bot, message)
            current_timestamp = int(time.time())
        finally:
            time.sleep(RETRY_TIME)


if __name__ == '__main__':
    main()
