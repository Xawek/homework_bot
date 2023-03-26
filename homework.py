import logging
import os
import time
from http import HTTPStatus

import requests
import telegram
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)


PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

RETRY_PERIOD = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}


HOMEWORK_VERDICTS = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}


def check_tokens():
    """Проверка токенов и id чата."""
    logger.debug('Проверка токенов и id чата.')
    return all((PRACTICUM_TOKEN, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID))


def send_message(bot, message):
    """Отправка сообщения в Telegram чат."""
    logger.debug('Отправка сообщения.')
    try:
        bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)
    except Exception:
        logger.error('Проблема с отправкой сообщения.')
    else:
        logger.debug('Сообщение отправлено.')


def get_api_answer(timestamp):
    """Запрос к эндпоинту."""
    logger.debug('Отправка запроса.')
    payload = {'from_date': timestamp}
    try:
        homework_status = requests.get(
            ENDPOINT, headers=HEADERS, params=payload)
    except Exception:
        logger.error('Ошибка запроса к API.')
    else:
        if homework_status.status_code != HTTPStatus.OK:
            raise requests.HTTPError('Нет ответа на запрос к API.',)
        return homework_status.json()


def check_response(response):
    """Проверка ответа API."""
    logger.debug('Проверка ответа API.')
    if 'homeworks' not in response:
        logger.error('В ответе API не содержится "homeworks".')
        raise TypeError()
    if not isinstance(response, dict):
        logger.error('В ответе API не содержится словарь.')
        raise TypeError()
    homeworks = response.get('homeworks')
    if not isinstance(homeworks, list):
        logger.error('В ответе API не содержится список.')
        raise TypeError()
    return homeworks


def parse_status(homework):
    """Извлечение точной информации о статусе домашней работы."""
    logger.debug('Извлечение информации')
    homework_name = homework.get('homework_name')
    homework_status = homework.get('status')
    if 'homework_name' not in homework:
        raise KeyError('Ответ не содержит homework_name.')
    if homework_status not in HOMEWORK_VERDICTS:
        raise ValueError(f'Ответ не содержит - {homework_status}')
    verdict = HOMEWORK_VERDICTS[homework_status]
    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def main():
    """Основная логика работы бота."""
    if not check_tokens():
        logger.critical('Проблема проверки токенов и id чата.')
        exit()
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    timestamp = int(time.time())
    prev_message = ''
    while True:
        try:
            response = get_api_answer(timestamp)
            homework = check_response(response)
            if homework:
                message = parse_status(homework[0])
                if prev_message != message:
                    send_message(bot, message)
                    prev_message = message
        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            if prev_message != message:
                send_message(bot, message)
                prev_message = message
        finally:
            time.sleep(RETRY_PERIOD)


if __name__ == '__main__':
    logging.basicConfig(
        level=logging.DEBUG,
        filename='bot.log',
        filemode='w',
        format='%(asctime)s, %(levelname)s, %(message)s, %(name)s',
        encoding='utf-8'
    )
    logger.addHandler(logging.StreamHandler())
    main()
