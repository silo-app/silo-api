from fastapi import APIRouter, Depends, HTTPException, Response, Cookie
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from jwt.exceptions import PyJWTError

from silo import config
from silo.log import logger
from silo.database import async_get_db, models
from silo.schemas import Token
from silo.security.jwt import create_access_token, create_refresh_token, decode_token
from silo.security.authenticator_factory import create_authenticator
from silo.security.authenticator.exceptions import (
    BindError,
    InvalidCredentialsError,
    AuthenticationError,
    NotAllowedError,
    BindNotAllowedError,
    UserNotFound,
    AuthTimeoutError,
)


auth_router = APIRouter(prefix="/auth", tags=["auth"])


@auth_router.post(
    "/refresh",
    description="Refresh access token using refresh token",
    summary="Refresh access token",
)
async def refresh_token(refresh_token: str = Cookie(None)):
    if not refresh_token:
        raise HTTPException(status_code=401, detail="Missing refresh token")

    try:
        payload = decode_token(refresh_token)
        token_type = payload.get("type")
        if not token_type == "refresh":
            raise HTTPException(status_code=401, detail="Invalid token type")

        user_id = payload.get("sub")
        new_access_token = create_access_token(user_id)
        return {"access_token": new_access_token, "token_type": "bearer"}

    except PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token")


@auth_router.post(
    "/logout",
    description="Logout",
    summary="Logout",
)
async def logout(response: Response):
    response.delete_cookie("refresh_token")
    return {"detail": "Logged out"}


@auth_router.post(
    "/login",
    description="Get an access token using OAuth2 password flow",
    summary="Get an access token",
)
async def access_token(
    response: Response,
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: AsyncSession = Depends(async_get_db),
) -> Token:
    username = form_data.username
    password = form_data.password

    authenticator = create_authenticator()
    try:
        authenticate = authenticator.authenticate(username=username, password=password)
        if authenticate is False:
            raise InvalidCredentialsError()
    except InvalidCredentialsError:
        logger.info("Invalid credentials for user %s", username)
        raise HTTPException(status_code=401, detail="Invalid credentials")
    except AuthenticationError as e:
        logger.error("Error authenticating user %s: %s", username, e)
        raise HTTPException(status_code=503, detail=f"Error authenticating user: {e}")
    except UserNotFound:
        logger.info("The user %s does not exists in authenticator source", username)
        raise HTTPException(status_code=401, detail="User does not exists")
    except BindNotAllowedError:
        logger.error("Not allowed to fetch user data for user %s?", username)
        raise HTTPException(status_code=401, detail="Not allowed to fetch user data")
    except NotAllowedError:
        logger.error("The user %s is not allowed to login!", username)
        raise HTTPException(status_code=401, detail="Not allowed to fetch user data")
    except AuthTimeoutError as e:
        logger.error("Timeout error authenticating user %s: %s", username, e)
        raise HTTPException(status_code=503, detail="Timeout error")
    except BindError as e:
        logger.error("Error binding user %s: %s", username, e)
        raise HTTPException(status_code=401, detail=f"Error binding user: {e}")

    result = await session.scalars(
        select(models.User).where(models.User.username == username)
    )
    user = result.one_or_none()
    if user is None:
        user = models.User(username=username, is_active=True)
        session.add(user)
        await session.commit()
        await session.refresh(user)

    if not user.is_active:
        raise HTTPException(status_code=403, detail="User is inactive")

    access_token = create_access_token(sub=str(user.id))
    refresh_token = create_refresh_token(sub=str(user.id))
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=True,
        samesite="strict",
        max_age=config.refresh_token_expire_days * 24 * 3600,
    )

    return {"access_token": access_token, "token_type": "bearer"}
