import logging
import sys
import uuid
from contextvars import ContextVar

from fastapi import Request
from loguru import logger

from core.environment_config import settings

logger_request_id: ContextVar[uuid] = ContextVar("request_id")


async def logging_dependency(request: Request):
    request_id = request.headers.get("X-Request-Id", uuid.uuid4())
    logger_request_id.set(request_id)
    if "application/json" in request.headers.get("content-type", ""):
        local_logger = logger.bind(request_headers=dict(request.headers), request_body=await request.body())
        local_logger.info(
            {
                "method": request.method,
                "url": request.url.path,
            }
        )


def format_record(record: dict) -> str:
    record["extra"]["request_id"] = logger_request_id.get()
    if record["exception"]:
        return "{exception}"
    return "{message}"


class InterceptHandler(logging.Handler):
    def emit(self, record: logging.LogRecord):
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())


def init_logging():
    loggers = (logging.getLogger(name) for name in logging.root.manager.loggerDict)
    intercept_handler = InterceptHandler()
    for runners_logger in loggers:
        runners_logger.propagate = False
        runners_logger.handlers = [intercept_handler]

    logger_request_id.set(uuid.uuid4())
    logger.configure(
        handlers=[
            {
                "sink": sys.stdout,
                "level": logging.INFO,
                "format": format_record,
                "serialize": not settings.project.debug,
            }
        ]
    )
