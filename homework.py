import logging
import time

from os import environ, getenv

import requests
import telegram

from dotenv import load_dotenv

load_dotenv()

PRACTICUM_TOKEN = getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = getenv('TELEGRAM_CHAT_ID')

RETRY_TIME = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}


HOMEWORK_STATUSES = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}

logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.DEBUG
)


def check_tokens():
    if (
        ('PRACTICUM_TOKEN' in environ)
        and ('TELEGRAM_TOKEN' in environ)
        and ('TELEGRAM_CHAT_ID' in environ)
    ):
        return True
    else:
        logging.critical('Нет переменных окружения')
        return False


def send_message(bot, message):
    try:
        bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)
        logging.info(f'сообщение {message} отправлено')
    except Exception as error:
        logging.error(f'Ошибка {error} отправки сообщения')


def get_api_answer(current_timestamp):
    timestamp = current_timestamp
    params = {'from_date': timestamp}
    try:
        try:
            # Делаем GET-запрос к эндпоинту с заголовком headers и параметрами
            # params
            homework_statuses = requests.get(
                ENDPOINT,
                headers=HEADERS,
                params=params
            )
        except Exception as error:
            logging.error(f'эндпоинт недоступен. ошибка {error}')
        homework_statuses = homework_statuses.json()
        return homework_statuses
    except Exception as error:
        logging.error(f'Сбой запроса: {error}')


def check_response(response):
    if 'homeworks' in response.keys():
        return response['homeworks']
    else:
        logging.error('ключ "homeworks" отсутствует в ответе API')


def parse_status(homework):
    try:
        homework_name = homework['lesson_name']
        try:
            homework_status = homework['status']
            try:
                verdict = HOMEWORK_STATUSES[homework_status]
                return (f'''
                    Изменился статус проверки работы "{homework_name}".
                    {verdict}
                ''')
            except Exception as error:
                logging.error(f'''
                    Недокументированный статус домашней работы, ошибка {error}
                ''')
        except Exception as error:
            logging.error(f'''
                ключ "lesson_name" осутствует в ответе API, ошибка {error}
            ''')
    except Exception as error:
        logging.error(f'''
            ключ "lesson_name" осутствует в ответе API. Ошибка {error}
        ''')


def main():
    """Основная логика работы бота."""
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    current_timestamp = 0
    while True:
        try:
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
            for homework in homeworks:
                message = parse_status(homework)
                send_message(bot, message)
            current_timestamp = int(time.time())
            time.sleep(RETRY_TIME)

        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            logging.error(f'Сбой в работе программы: {error}')
            send_message(bot, message)
            time.sleep(RETRY_TIME)


if __name__ == '__main__':
    main()
