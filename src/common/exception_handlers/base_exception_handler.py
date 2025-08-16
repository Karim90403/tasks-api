from fastapi import Response
from fastapi.responses import ORJSONResponse
from fastapi_request_id import BaseExceptionHandler, get_request_id
from loguru import logger
from starlette.requests import Request


class RequestIdJsonExceptionHandler(BaseExceptionHandler):
    status_code = None
    detail = "{msg}: {params}"
    exception = None

    def build_response(self, request: Request, exc: Exception) -> Response:
        msg = self.detail
        if hasattr(exc, "exceptions"):
            logger.error(exc.exceptions.__str__())
        else:
            logger.error(str(exc))

        if hasattr(exc, "params") and exc.params.items():
            params = ", ".join(f"{key} - {value}" for key, value in exc.params.items())
            msg = msg.format(msg=exc.args[0], params=params)
        else:
            msg = "{msg}"
            msg = msg.format(msg=exc.args[0])

        return ORJSONResponse(
            status_code=self.status_code,
            content={
                "error": self.status_code >= 500,
                "detail": msg,
                "request_id": get_request_id(),
            },
        )
