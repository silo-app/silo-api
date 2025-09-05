import fnmatch
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from jwt.exceptions import PyJWTError
from silo.database import async_get_db, models
from silo.security.jwt import decode_token
from silo.schemas import UserRead

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


async def get_current_user(
    token: str = Depends(oauth2_scheme), session: AsyncSession = Depends(async_get_db)
) -> UserRead:
    credentials_exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_token(token)
        user_id = payload.get("sub")
        if not user_id:
            raise credentials_exc
    except PyJWTError:
        raise credentials_exc

    result_u = await session.execute(
        select(models.User)
        .options(selectinload(models.User.roles))
        .where(models.User.id == int(user_id))
    )
    user: models.User | None = result_u.scalars().first()
    if not user or not user.is_active:
        raise credentials_exc

    return UserRead.model_validate(user)


def require_permission():
    async def dependency(request: Request, current_user=Depends(get_current_user)):
        path = request.url.path
        method = request.method.upper()

        allowed = False
        for role in current_user.roles:
            if not role.permissions:
                continue
            for pattern, methods in role.permissions.items():
                if fnmatch.fnmatch(path, pattern):
                    if method in methods:
                        allowed = True
                        break
            if allowed:
                break

        if not allowed:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Not allowed to {method} {path}",
            )
        return current_user

    return dependency
