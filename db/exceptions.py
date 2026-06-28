import logging

logger = logging.getLogger(__name__)


class DatabaseException(Exception):
    def __init__(self, message: str, code: int, original_error: Exception = None):
        super().__init__(message)
        self.message = message
        self.original_error = original_error
        self.code = code
