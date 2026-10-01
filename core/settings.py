from datetime import datetime
from os import getenv
from zoneinfo import ZoneInfo

from dotenv import load_dotenv

from core.env_path import Env_path

load_dotenv(Env_path)


class Settings:
    DB_URL = getenv('DB_URL')
    ADMIN_USERNAME = getenv('ADMIN_USERNAME')
    ADMIN_PASSWORD = getenv('ADMIN_PASSWORD')


UZB_TZ = ZoneInfo("Asia/Tashkent")


def get_current_uzb_time() -> datetime:
    return datetime.now(UZB_TZ)
