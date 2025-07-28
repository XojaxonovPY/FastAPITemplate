import os

from dotenv import load_dotenv

from utils.env_path import Env_path

load_dotenv(Env_path)


class Settings:
    DB_URL = os.getenv('DB_URL')
