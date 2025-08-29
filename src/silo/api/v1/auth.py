from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from silo.database import async_get_db, models
from silo.schemas import Token
from silo.security.jwt import create_access_token
from silo.security.authenticator_factory import create_authenticator
from silo.security.authenticator.exceptions import (
    InvalidCredentialsError,
    AuthenticationError,
)


auth_router = APIRouter(prefix="/auth", tags=["auth"])


@auth_router.post(
    "/token",
    description="Get an access token using OAuth2 password flow",
    summary="Get an access token",
)
async def access_token(
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

    if user.is_active == False:
        raise HTTPException(status_code=403, detail="User is inactive")

    access_token = create_access_token(sub=str(user.id))
    return {"access_token": access_token, "token_type": "bearer"}
