from typing import TypedDict


class AuthData(TypedDict):
    username: str | None = None
    password: str


class UserAttributes(TypedDict):
    username: str
    groups: list
    mail: str | None
    display_name: str | None
