from fastapi import status

from common.exception_handlers.base_exception_handler import RequestIdJsonExceptionHandler
from common.exceptions.authorisation import AuthorisationException


class AuthorisationExceptionHandler(RequestIdJsonExceptionHandler):
    status_code = status.HTTP_401_UNAUTHORIZED
    message = "Authorisation exception"
    exception = AuthorisationException

class UnexpectedExceptionHandler(RequestIdJsonExceptionHandler):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    message = "Unexpected exception"
    exception = Exception
