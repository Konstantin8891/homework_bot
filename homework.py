import logging
import time

from http import HTTPStatus

import requests
import telegram

from dotenv import load_dotenv

from config import (PRACTICUM_TOKEN, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID,
                    RETRY_TIME, ENDPOINT, HEADERS, HOMEWORK_STATUSES)

load_dotenv()

logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.DEBUG
)


def check_tokens():
    """Тест переменных окружения."""
    if (
        (PRACTICUM_TOKEN is not None)
        and (TELEGRAM_TOKEN is not None)
        and (TELEGRAM_CHAT_ID is not None)
    ):
        return True


def send_message(bot, message):
    """Отправка сообщения."""
    try:
        bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)
        logging.info(f'сообщение {message} отправлено')
    except Exception as error:
        logging.error(f'Ошибка {error} отправки сообщения')


def get_api_answer(current_timestamp):
    """Гет запрос к конечной точке."""
    timestamp = current_timestamp
    params = {'from_date': timestamp}
    # Делаем GET-запрос к эндпоинту с заголовком headers и параметрами
    # params
    homework_statuses = requests.get(
        ENDPOINT,
        headers=HEADERS,
        params=params
    )
    if homework_statuses.status_code != HTTPStatus.OK:
        logging.error(f'Ошибка ответа. Код {homework_statuses.status_code}')
        raise Exception(f'Ошибка ответа. Код {homework_statuses.status_code}')
    homework_statuses = homework_statuses.json()
    return homework_statuses


def check_response(response):
    """Проверка ответа."""
    if type(response) is not dict:
        logging.error('ошибка типа ответа API')
        raise TypeError('ответ не является словарём')
    if 'homeworks' in response.keys():
        homeworks = response['homeworks']
        if type(homeworks) is list:
            return homeworks
    else:
        logging.error('ключ "homeworks" отсутствует в ответе API')
        raise Exception('ключ "homeworks" отсутствует в ответе API')


def parse_status(homework):
    """Парсинг ответа."""
    homework_name = homework['homework_name']
    homework_status = homework['status']
    if homework_name is None or homework_status is None:
        logging.error('отсутствие ключей в словаре homework')
        raise Exception('отсутствие ключей в словаре homework')
    try:
        verdict = HOMEWORK_STATUSES[homework_status]
        return (
            f'Изменился статус проверки работы "{homework_name}".'
            f'{verdict}'
        )
    except Exception as error:
        logging.error(
            f'Недокументированный статус домашней работы, ошибка {error}'
        )
        raise (f'Недокументированный статус домашней работы, ошибка {error}')


def main():
    """Основная логика работы бота."""
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    current_timestamp = 0
    while True:
        if check_tokens():
            response = get_api_answer(current_timestamp)
        else:
            break
        homeworks = check_response(response)
        empty_list = list()
        if homeworks == empty_list:
            logging.debug('''
                отсутствуют изменения состояний проверки домашних заданий
            ''')
        try:
            for homework in homeworks:
                message = parse_status(homework)
                send_message(bot, message)
            current_timestamp = int(time.time())
            time.sleep(RETRY_TIME)

        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            logging.error(f'Сбой в работе программы: {error}')
            send_message(bot, message)
            raise Exception
            time.sleep(RETRY_TIME)


if __name__ == '__main__':
    main()
