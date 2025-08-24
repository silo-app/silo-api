from datetime import timedelta
from typing import Annotated
from fastapi import APIRouter, Depends, Response, HTTPException
from fastapi.security import OAuth2PasswordRequestForm

from silo.schemas import Token

# from silo.auth.ldap import LDAP
from silo import config

login_router = APIRouter(tags=["login"])
logout_router = APIRouter(tags=["logout"])


@login_router.post("/login", response_model=Token)
async def login_for_access_token(
    response: Response,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> dict[str, str]:

    user = {
        "username": "mawi",
        "email": "kontakt@marcelwilkowsky.de",
        "full_name": "Marcel-Brian Wilkowsky",
    }

    # TODO: LDAP authentication

    if not user:
        raise HTTPException(401, "Unauthorized")

    access_token_expires = timedelta(minutes=config.access_token_expire_minutes)
    access_token = await create_access_token(
        data={"sub": user["username"]}, expires_delta=access_token_expires
    )

    refresh_token = await create_refresh_token(data={"sub": user["username"]})
    max_age = config.refresh_token_expire_days * 24 * 60 * 60

    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=max_age,
    )

    return {"access_token": access_token, "token_type": "bearer"}
