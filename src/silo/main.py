from fastapi import Depends, FastAPI, HTTPException, Request
import fnmatch
from fastapi.exception_handlers import http_exception_handler
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from silo.api import router
from silo import config
from silo.api.dependencies import get_current_user, require_permission
from silo.log import logger
from starlette.middleware.base import BaseHTTPMiddleware


from silo.database import async_engine
from silo.database.models import Base
from silo.security.jwt import verify_token


async def add_admin_user() -> None:
    pass


async def create_tables() -> None:
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


@asynccontextmanager
async def db_lifespan(app: FastAPI):

    # create database tables
    await create_tables()

    # initialize admin user
    await add_admin_user()

    logger.info("Started SILO application")

    yield


app: FastAPI = FastAPI(
    title="SILO API",
    lifespan=db_lifespan,
    version=config.api_version,
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
