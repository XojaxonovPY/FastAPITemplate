import logging

logger = logging.getLogger(__name__)


class DatabaseException(Exception):
    def __init__(self, message: str, code: int):
        self.message = message
        self.code = code
        super().__init__(message, code)
