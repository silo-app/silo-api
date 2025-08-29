class InvalidCredentialsError(Exception):
    pass


class AuthenticationError(Exception):
    pass


class NotAllowedError(Exception):
    pass


class TimeoutError(Exception):
    pass
