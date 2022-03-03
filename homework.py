import os
import time
import telegram
import requests
from dotenv import load_dotenv
import logging
from http import HTTPStatus

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
RETRY_TIME = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}
HOMEWORK_STATUSES = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.',
}


def send_message(bot, message):
    """Отправляет сообщение в Телеграм."""
    bot.send_message(TELEGRAM_CHAT_ID, message)
    logging.info('Отправлено сообщение в Телеграм')


def get_api_answer(current_timestamp):
    """Направляет запрос к API ЯндексПрактикума,возращает ответ."""
    params = {'from_date': current_timestamp}
    response = requests.get(
        ENDPOINT,
        headers=HEADERS,
        params=params,
    )
    if response.status_code != HTTPStatus.OK:
        raise Exception('Недоступность эндпоинта')
    return response.json()


def check_response(response):
    """Возвращает содержимое в ответе от ЯндексПрактикума."""
    if isinstance(response, list):
        response = response[0]
    homework = response.get('homeworks')
    if homework is None:
        raise Exception('API не содержит ключа homeworks')
    if not isinstance(homework, list):
        raise Exception('Ответ не в виде списка')
    return homework


def parse_status(homework):
    """Извлекает статус работы из ответа ЯндексПракутикум."""
    homework_name = homework.get('homework_name')
    homework_status = homework.get('status')
    if homework_status is None or homework_name is None:
        raise Exception('Отсутсвуют ключи homework_name или status')
    verdict = HOMEWORK_STATUSES.get(homework_status)
    if verdict is None:
        raise Exception('Статус не обнаружен')
    return f'Изменился статус проверки работы "{homework_name}". {verdict}'
   

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
        raise Exception('Не обнаружены все необходимые ключи!')
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    current_timestamp = int(time.time())
    while True:
        try:
            response = get_api_answer(current_timestamp)
            print(response)
            homeworks = check_response(response)
            if homeworks:
                message = parse_status(homeworks[0])
                send_message(bot, message)
            current_timestamp = int(time.time())
            time.sleep(RETRY_TIME)
        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            logging.error(message)
            send_message(bot, message)
            time.sleep(RETRY_TIME)


if __name__ == '__main__':
    main()
