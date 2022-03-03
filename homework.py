import os
import time
import telegram
import requests
from dotenv import load_dotenv
import logging

load_dotenv()

logger = logging.getLogger()
handler = logging.StreamHandler()
formatter = logging.Formatter(
    '%(asctime)s - [%(levelname)s] - %(message)s - %(funcName)s'
)
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
RETRY_TIME = 15
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}
HOMEWORK_STATUSES = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}


def send_message(bot, message):
    """Отправляет сообщение в Телеграм."""
    try:
        bot.send_message(TELEGRAM_CHAT_ID, message)
        logging.info('Отправлено сообщение в Телеграм')
    except Exception as error:
        logging.error(f'Cбой при отправке сообщения в Telegram: {error}')


def get_api_answer(current_timestamp):
    """Направляет запрос к API ЯндексПрактикума,возращает ответ."""
    timestamp = current_timestamp
    params = {'from_date': int(timestamp)}
    try:
        response = requests.get(
            ENDPOINT,
            headers=HEADERS,
            params=params,
            verify=False
        )
        return response
    except Exception as error:
        logging.error(f'Недоступность эндпоинта ЯндексПрактикум: {error}')


def check_response(response):
    """Возвращает содержимое в ответе от ЯндексПрактикума."""
    try:
        return response.json().get('homeworks')
    except Exception as error:
        logging.error(f'Отсутсвует ключ homeworks: {error}')


def parse_status(homework):
    """Извлекает статус работы из ответа ЯндексПракутикум."""
    try:
        homework_name = homework.get('homework_name')
        homework_status = homework.get('status')
    except Exception as error:
        logging.error(f'Отсутсвуют ключи homework_name или status: {error}')
        return 'Ошибка: отсутсвуют ключи homework_name или status'
    try:
        verdict = HOMEWORK_STATUSES.get(homework_status)
        return f'Изменился статус проверки работы "{homework_name}". {verdict}'
    except Exception as error:
        logging.error(
            f'Недокументированный статус домашней работы,\
             обнаруженный в ответе: {error}'
        )


def check_tokens():
    """Проверяет наличие токенов."""
    flag = (
        PRACTICUM_TOKEN is not None
        and TELEGRAM_TOKEN is not None
        and TELEGRAM_CHAT_ID is not None
    )
    return flag


def main():
    """Основная логика работы бота."""
    if not check_tokens():
        logging.critical('Не обнаружены все необходимые ключи!')
        return 'Конец'
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    current_timestamp = 1645026685
    while True:
        try:
            response = get_api_answer(current_timestamp)
            homeworks = check_response(response)
            if homeworks:
                message = parse_status(homeworks[0])
                print(message)
                send_message(bot, message)
            current_timestamp += 5  # int(time.time())
            time.sleep(RETRY_TIME)
        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            logging.error(message)
            current_timestamp += 5
            time.sleep(RETRY_TIME)


if __name__ == '__main__':
    main()
