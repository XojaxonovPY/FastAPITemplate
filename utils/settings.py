from os import getenv

from dotenv import load_dotenv

from utils.env_path import Env_path

load_dotenv(Env_path)


class Settings:
    DB_URL = getenv('DB_URL')
    ADMIN_USERNAME = getenv('ADMIN_USERNAME')
    ADMIN_PASSWORD = getenv('ADMIN_PASSWORD')
