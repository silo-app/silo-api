from fastapi import APIRouter, Depends, HTTPException, Response, Cookie
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from jwt.exceptions import PyJWTError

from silo import config
from silo.database import async_get_db, models
from silo.schemas import Token
from silo.security.jwt import create_access_token, create_refresh_token, decode_token
from silo.security.authenticator_factory import create_authenticator
from silo.security.authenticator.exceptions import (
    InvalidCredentialsError,
    AuthenticationError,
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
        authenticate = authenticator.authenticate(username, password)
        if authenticate is False:
            raise InvalidCredentialsError()
    except InvalidCredentialsError:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    except AuthenticationError:
        raise HTTPException(status_code=401, detail="Error authenticating user")

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
