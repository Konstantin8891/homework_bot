import os.path

from os import getenv

from dotenv import load_dotenv

load_dotenv()

PRACTICUM_TOKEN = getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = getenv('TELEGRAM_CHAT_ID')

RETRY_TIME = 1200
ENDPOINT_API = 'https://practicum.yandex.ru/api/'
API = 'user_api/'
METHOD_STAT = 'homework_statuses/'
ENDPOINT = os.path.join(ENDPOINT_API, API, METHOD_STAT)
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}

HOMEWORK_STATUSES = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}
