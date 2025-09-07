from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import HttpUrl, Field, SecretStr, PostgresDsn
from pathlib import Path
from typing import Type


# from silo.security.authenticator import LDAPAuthenticator

THIS_PARENT_DIR = Path(__file__).parent.resolve()


class AppConfig(BaseSettings):
    app_name: str = "SILO"
    version: str = "0.0.1"
    api_version: str = "v1"

    debug_mode: bool = False
    dev_mode: bool = False

    first_admin_user: str | None = None

    allowed_origins: list[HttpUrl] = ["http://localhost:3000"]
    allowed_paths_without_auth: list[str] = [
        "/openapi.json",
        "/redoc",
        "/docs",
        "/static/favicon.png",
        "/static/logo.png",
        "/api/version",
        "/api/v1/auth/login",
        "/api/auth/login",
    ]

    # postgresql+asyncpg://<db_username>:<db_secret>@<db_host>:<db_port>/<db_name>
    postgres_database_uri: PostgresDsn = (
        "postgresql+asyncpg://silo_db_user:silo@localhost:5432/silo"
    )

    # logging
    log_level: str = Field(default="INFO")
    log_directory: str = Field(default=f"{THIS_PARENT_DIR}/log/logs")

    # authentication / authorization

    authenticator_class: Type | str = "silo.security.authenticator.LDAPAuthenticator"

    ldap_server_uri: str
    ldap_connect_timeout: int = 5  # seconds
    ldap_receive_timeout: int = 10  # seconds
    ldap_base_dn: str
    ldap_user_dn_template: str
    ldap_use_ssl: bool = True
    ldap_base_user_dn: str | None = None
    ldap_user_search_filter: str = "(uid={username})"
    ldap_allowed_groups: list[str] | None = None

    ldap_username_attribute: str = "uid"
    ldap_mail_attribute: str = "mail"
    ldap_groups_attribute: str = "memberOf"
    ldap_display_name_attribute: str = "cn"

    ldap_ssl_skip_verify: bool = False
    ldap_bind_dn: str | None = None
    ldap_bind_pw: str | None = None

    access_token_expire_minutes: int = 60
    refresh_token_expire_days: int = 7
    jwt_algorithm: str = "HS256"
    secret_key: SecretStr

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="silo_",
    )


config = AppConfig()
