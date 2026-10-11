class UserAlreadyExistsError(Exception):
    pass


class UserNotFoundError(Exception):
    pass


class UpdateUserNeedFields(Exception):
    pass
