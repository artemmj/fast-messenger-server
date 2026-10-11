from fastapi import HTTPException


class WrongEmailPasswordException(HTTPException):
    pass


class AccountDisabledOrBannedException(HTTPException):
    pass
