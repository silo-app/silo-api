from fastapi import FastAPI, HTTPException, Request
import fnmatch
from fastapi.exception_handlers import http_exception_handler
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from sqlalchemy import select
from sqlalchemy.exc import MultipleResultsFound
from silo.api import router
from silo import config
from silo.log import logger

from silo.database import async_engine, async_get_db
from silo.database.models import Base, Role, User
from silo.security.jwt import verify_token


async def add_default_role() -> None:
    async for db in async_get_db():
        # user role
        result = await db.execute(select(Role).filter_by(name="user"))
        user_role = result.scalar_one_or_none()
        if user_role is None:
            db.add(Role(name="user", permissions={"/user/myinfo": ["GET"]}))
            await db.commit()
            print("[SILO] Added default role 'user'")
        # admin role
        result = await db.execute(select(Role).filter_by(name="admin"))
        admin_role = result.scalar_one_or_none()
        if admin_role is None:
            db.add(
                Role(name="admin", permissions={"*": ["GET", "POST", "PUT", "DELETE"]})
            )
            await db.commit()
            print("[SILO] Added default role 'admin'")


async def add_admin_user() -> None:
    async for db in async_get_db():
        result = await db.execute(
            select(User).where(User.roles.any(Role.name == "admin"))
        )
        try:
            admin_user = result.scalar_one_or_none()
            if admin_user is None:
                if config.first_admin_user is None:
                    raise RuntimeError(
                        "[SILO] Error: Cannot startup SILO. Define a first admin user with the environment variable FIRST_ADMIN_USER"
                    )
                new_user = User(username=config.first_admin_user)
                resultr = await db.execute(select(Role).where(Role.name == "admin"))
                admin_role = resultr.scalar_one_or_none()

                new_user.roles.append(admin_role)
                db.add(new_user)
                await db.commit()

                print(f"[SILO] Added default admin user '{config.first_admin_user}'")
        except MultipleResultsFound:
            pass


async def create_tables() -> None:
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


@asynccontextmanager
async def db_lifespan(app: FastAPI):

    # create database tables
    await create_tables()

    # Adding default roles
    await add_default_role()

    # initialize admin user
    await add_admin_user()

    logger.info("[SILO] Application startup complete")

    yield


app: FastAPI = FastAPI(
    title="SILO API",
    lifespan=db_lifespan,
    version=config.api_version,
    contact={
        "name": "Marcel-Brian Wilkowsky",
        "url": "https://mawidev.de",
        "email": "kontakt@marcelwilkowsky.de",
    },
    license_info={
        "name": "MIT license",
        "url": "https://opensource.org/licenses/MIT",
    },
    swagger_ui_parameters={
        "syntaxHighlight": {"theme": "obsidian"},
        "docExpansion": "none",
    },
    responses={
        401: {
            "description": "Unauthorized",
            "content": {"application/json": {"example": {"detail": "Unauthorized"}}},
        },
        403: {
            "description": "Forbidden",
            "content": {"application/json": {"example": {"detail": "Forbidden"}}},
        },
    },
)

app.include_router(router)

API_PREFIX = f"{router.prefix}/{config.api_version}"


# application middleware
@app.middleware("http")
async def http_auth_middleware(request: Request, call_next):
    logger.info(f"Incoming request: {request.method} {request.url}")

    request_path = request.url.path
    path = (
        request_path[len(API_PREFIX) :]
        if request_path.startswith(API_PREFIX)
        else request_path
    )
    if not path.startswith("/"):
        path = "/" + path

    if path in config.allowed_paths_without_auth:
        return await call_next(request)

    for allowed in config.allowed_paths_without_auth:
        if fnmatch.fnmatch(path, allowed):
            return await call_next(request)

    try:
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Unauthorized")

        # token without "Bearer "
        token = auth_header[7:]
        # verify token
        request.state.current_user_payload = await verify_token(token)

        response = await call_next(request)
        return response
    except HTTPException as exc:
        return await http_exception_handler(request, exc)


app.add_middleware(
    CORSMiddleware,
    allow_origins=config.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
