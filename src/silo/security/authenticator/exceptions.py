class InvalidCredentialsError(Exception):
    pass


class AuthenticationError(Exception):
    pass


class BindError(Exception):
    pass


class NotAllowedError(Exception):
    pass


class AuthTimeoutError(Exception):
    pass


class UserNotFound(Exception):
    pass
