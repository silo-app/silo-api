from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from silo.api import router
from silo import config
from silo.log import logger

# from silo.auth.ldap import LDAP
# from silo.auth.auth import Auth

from silo.database import async_engine
from silo.database.models import Base


async def create_tables() -> None:
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


@asynccontextmanager
async def db_lifespan(app: FastAPI):

    # create database tables
    await create_tables()

    # Initialize LDAP
    # ldap_auth = LDAP(config.ldap_server_uri, config.ldap_base_dn)
    # auth_service = Auth(app.db, ldap_auth)

    # app.dependency_overrides[Auth] = lambda: auth_service

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
)

app.include_router(router)


# application middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.debug(f"Incoming request: {request.method} {request.url}")
    response = await call_next(request)
    logger.debug(f"Response status: {response.status_code}")
    return response


app.add_middleware(
    CORSMiddleware,
    allow_origins=config.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
