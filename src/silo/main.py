import pathlib
import fnmatch
from fastapi import FastAPI, HTTPException, Request
from fastapi.exception_handlers import http_exception_handler
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager

from silo.api import router
from silo import config
from silo.log import logger
from silo.security.jwt import verify_token
from silo.startup import create_tables, add_default_roles, add_default_admin
from silo.security.authenticator_factory import create_authenticator


@asynccontextmanager
async def db_lifespan(app: FastAPI):
    # check authentication class configuration
    create_authenticator()
    # by calling create_authenticator an instance will be created and if the class is misconfigured a TypeError will be thrown

    # create database tables
    await create_tables()

    # Adding default roles
    await add_default_roles()

    # initialize admin user
    await add_default_admin()

    logger.info("[SILO] Application startup complete")

    yield


app: FastAPI = FastAPI(
    title="SILO API",
    lifespan=db_lifespan,
    version=config.api_version,
    description=f"**Latest API version (default): {config.api_version}**</br></br>**/api -> /api/{config.api_version}**</br></br>Call **/api/version** to check available and the latest version.",
    contact={
        "name": "Marcel-Brian Wilkowsky",
        "url": "https://silo.mawidev.de",
        "email": "kontakt@marcelwilkowsky.de",
    },
    license_info={
        "name": "MIT license",
        "url": "https://opensource.org/licenses/MIT",
    },
    swagger_ui_parameters={
        "syntaxHighlight": {"theme": "obsidian"},
        "docExpansion": "none",
        "displayRequestDuration": True,
        "filter": True,
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

static_path = pathlib.Path(__file__).parent / "static"
app.mount("/static", StaticFiles(directory=static_path), name="static")


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
    allow_origins=[str(url).rstrip("/") for url in config.allowed_origins],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
