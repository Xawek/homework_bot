import logging
import os
import time
from http import HTTPStatus

import exceptions
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
    logger.info('Отправка сообщения.')
    try:
        bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)
    except Exception as error:
        error_message = f'Проблема с отправкой сообщения.{error}'
        logger.error(error_message)
    else:
        logger.debug('Сообщение отправлено.')


def get_api_answer(timestamp):
    """Запрос к эндпоинту."""
    payload = {'from_date': timestamp}
    request_items = {
        'url': ENDPOINT,
        'headers': HEADERS,
        'params': payload,
    }
    logger.info('Отправка запроса.')
    try:
        homework_status = requests.get(**request_items)
    except Exception as error:
        raise exceptions.ConnectionError(
            f'Эндоинт не доступен.'
            f'Параметры запроса:{request_items} ошибка:{error}'
        )
    else:
        if homework_status.status_code != HTTPStatus.OK:
            code = homework_status.status_code
            text = homework_status.text
            error_info = f'Код: {code}, ответ: {text}'
            if homework_status.status_code == HTTPStatus.BAD_REQUEST:
                raise exceptions.ResponseProblemException(
                    f'Некорректный запрос. {error_info}'
                )
            if homework_status.status_code == HTTPStatus.UNAUTHORIZED:
                raise exceptions.ResponseProblemException(
                    f'Не авторизованный запрос. {error_info}'
                )
            if homework_status.status_code == HTTPStatus.INTERNAL_SERVER_ERROR:
                raise exceptions.ResponseProblemException(
                    f'Внутренняя ошибка сервера. {error_info}'
                )
            else:
                raise requests.HTTPError('Нет ответа на запрос к API.',)
        return homework_status.json()


def check_response(response):
    """Проверка ответа API."""
    logger.info('Проверка ответа API.')
    if 'homeworks' not in response:
        raise TypeError('В ответе API не содержится "homeworks".')
    if not isinstance(response, dict):
        raise TypeError('В ответе API не содержится словарь.')
    homeworks = response.get('homeworks')
    if not isinstance(homeworks, list):
        raise TypeError('В ответе API не содержится список.')
    return homeworks


def parse_status(homework):
    """Извлечение точной информации о статусе домашней работы."""
    logger.info('Извлечение информации')
    homework_status = homework.get('status')
    if 'homework_name' not in homework:
        raise KeyError('Ответ не содержит homework_name.')
    if homework_status not in HOMEWORK_VERDICTS:
        raise ValueError(f'Ответ не содержит - {homework_status}')
    verdict = HOMEWORK_VERDICTS[homework_status]
    homework_name = homework.get('homework_name')
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
            logger.error(message)
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
