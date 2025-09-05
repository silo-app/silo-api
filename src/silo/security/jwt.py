from datetime import datetime, timezone, timedelta
from fastapi import HTTPException
from fastapi.security import OAuth2PasswordBearer
import jwt
from jwt.exceptions import PyJWTError

from silo import config

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token")


def create_access_token(sub: str) -> str:
    payload = {
        "sub": sub,
        "exp": datetime.now(timezone.utc)
        + timedelta(minutes=config.access_token_expire_minutes),
        "iat": datetime.now(timezone.utc),
    }
    return jwt.encode(payload, str(config.secret_key), algorithm=config.jwt_algorithm)


def decode_token(token: str) -> dict:
    return jwt.decode(token, str(config.secret_key), algorithms=[config.jwt_algorithm])


async def verify_token(token: str) -> dict:
    try:
        payload = jwt.decode(
            token, str(config.secret_key), algorithms=[config.jwt_algorithm]
        )
        user_id: str = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token")

        exp = payload.get("exp")
        if exp:
            exp_datetime = datetime.fromtimestamp(exp, tz=timezone.utc)
            now = datetime.now(timezone.utc)
            if exp_datetime < now:
                raise HTTPException(status_code=401, detail="Token expired")

        return {"user_id": user_id, "payload": payload}

    except PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")


def create_refresh_token(sub: str) -> str:
    payload = {
        "sub": sub,
        "exp": datetime.now(timezone.utc)
        + timedelta(days=config.refresh_token_expire_days),
        "iat": datetime.now(timezone.utc),
    }
    return jwt.encode(payload, str(config.secret_key), algorithm=config.jwt_algorithm)
