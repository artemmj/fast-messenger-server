from fastapi import HTTPException


class WrongEmailPasswordException(HTTPException):
    pass


class AccountDisabledOrBannedException(HTTPException):
    pass


class WebSocketAuthError(Exception):
    pass
