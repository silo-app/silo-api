from datetime import UTC, datetime, timedelta
from typing import Any
from enum import Enum
from jwt.exceptions import PyJWTError

import jwt

from silo import config
from silo.schemas.Token import TokenData

class TokenType(str, Enum):
    ACCESS = "access"
    REFRESH = "refresh"

async def create_access_token(data: dict[str, Any], expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(UTC).replace(tzinfo=None) + expires_delta
    else:
        expire = datetime.now(UTC).replace(tzinfo=None) + timedelta(minutes=config.access_token_expire_minutes)
    to_encode.update({"exp": expire, "token_type": TokenType.ACCESS})
    encoded_jwt: str = jwt.encode(to_encode, config.secret_key.get_secret_value(), algorithm=config.jwt_algorithm)
    return encoded_jwt


async def create_refresh_token(data: dict[str, Any], expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(UTC).replace(tzinfo=None) + expires_delta
    else:
        expire = datetime.now(UTC).replace(tzinfo=None) + timedelta(days=config.refresh_token_expire_days)
    to_encode.update({"exp": expire, "token_type": TokenType.REFRESH})
    encoded_jwt: str = jwt.encode(to_encode, config.secret_key.get_secret_value(), algorithm=config.jwt_algorithm)
    return encoded_jwt

async def verify_token(token: str, expected_token_type: TokenType) -> TokenData | None:
    """Verify a JWT token and return TokenData if valid.

    Parameters
    ----------
    token: str
        The JWT token to be verified.
    expected_token_type: TokenType
        The expected type of token (access or refresh)

    Returns
    -------
    TokenData | None
        TokenData instance if the token is valid, None otherwise.
    """

    try:
        payload = jwt.decode(token, config.secret_key.get_secret_value(), algorithms=[config.jwt_algorithm])
        username: str | None = payload.get("sub")
        token_type: str | None = payload.get("token_type")

        if username is None or token_type != expected_token_type:
            return None

        return TokenData(username_or_email=username)

    except PyJWTError:
        return None
