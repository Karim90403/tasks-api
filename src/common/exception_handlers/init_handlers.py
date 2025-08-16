from fastapi import FastAPI
from loguru import logger

from common.exception_handlers.base_exception_handler import RequestIdJsonExceptionHandler


def init_handlers(app: FastAPI):
    try:
        exception_classes = RequestIdJsonExceptionHandler.__subclasses__()
        for exception_class in exception_classes:
            exception = exception_class()
            app.add_exception_handler(exception.exception, exception)
    except Exception as e:
        logger.error(e)
