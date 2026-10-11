class ChatNotFoundError(Exception):
    pass


class ChatAccessDeniedError(Exception):
    pass


class PersonalChatAlreadyExistsError(Exception):
    pass


class GroupChatNeedNameError(Exception):
    pass


class ChatLimitExceededError(Exception):
    pass
