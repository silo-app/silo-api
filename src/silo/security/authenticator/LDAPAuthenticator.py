from ssl import CERT_NONE
from ldap3 import Connection, Server, Tls, ALL
from ldap3.utils.conv import escape_filter_chars
from ldap3.core.exceptions import (
    LDAPSocketOpenError,
    LDAPInvalidCredentialsResult,
    LDAPNoSuchObjectResult,
    LDAPInsufficientAccessRightsResult,
    LDAPBindError,
    LDAPResponseTimeoutError,
)

from silo import config
from silo.log import logger
from silo.schemas import AuthData, UserAttributes
from silo.security.authenticator import BaseAuthenticator
from silo.security.authenticator.exceptions import (
    AuthTimeoutError,
    AuthenticationError,
    BindError,
    InvalidCredentialsError,
    NotAllowedError,
    UserNotFound,
)


class LDAPAuthenticator(BaseAuthenticator):
    def __init__(
        self,
        server_uri: str,
        base_dn: str,
        user_dn_template: str,
        bind_dn: str,
        bind_pw: str,
        allowed_groups: list[str],
        use_ssl: bool,
        ssl_skip_verify: bool,
    ):
        self.server_uri = server_uri
        self.base_dn = base_dn
        self.user_dn_template = user_dn_template
        self.bind_dn = bind_dn
        self.bind_pw = bind_pw
        self.allowed_groups = allowed_groups
        self.use_ssl = use_ssl
        self.ssl_skip_verify = ssl_skip_verify

        tls = None
        if self.ssl_skip_verify is True:
            tls = Tls(validate=CERT_NONE)

        self.server = Server(
            self.server_uri,
            use_ssl=self.use_ssl,
            tls=tls,
            connect_timeout=config.ldap_connect_timeout,
            get_info=ALL,
        )

    def authenticate(
        self, return_user_attributes: bool = False, **kwargs: AuthData
    ) -> bool | UserAttributes:
        username = kwargs.get("username")
        password = kwargs.get("password")
        escaped_username = escape_filter_chars(username, "utf-8")
        user_dn = self.user_dn_template.format(username=escaped_username)

        try:
            # Even if return_user_attributes is False, lets check the user data with given bind dn/password
            # If the search filter has a filter for e.g. locked users, it will raise an exception
            user_data = self.get_user_attributes(username)

            user_connection = Connection(
                self.server,
                user=user_dn,
                password=password,
                receive_timeout=config.ldap_receive_timeout,
                raise_exceptions=True,
            )

            if user_connection.bind():
                user_connection.unbind()
                logger.info(
                    "[LDAPAuhtenticator] Successfully authenticated user %s", username
                )
                logger.error("[LDAPAuthenticator] User data: %s", user_data)
                if return_user_attributes is True:
                    return user_data

                return True

        except LDAPInvalidCredentialsResult:
            raise InvalidCredentialsError()
        except LDAPNoSuchObjectResult:
            raise UserNotFound()
        except LDAPInsufficientAccessRightsResult:
            raise NotAllowedError()
        except LDAPResponseTimeoutError:
            raise TimeoutError()
        except LDAPSocketOpenError as e:
            raise AuthTimeoutError(e)
        except LDAPBindError as e:
            raise BindError(e)
        except Exception as e:
            raise AuthenticationError(e)

        return False

    def get_user_attributes(self, username) -> UserAttributes:
        # use a bind user to fetch user attributes (anonymous bind if no one given)
        connection = Connection(
            self.server,
            user=config.ldap_bind_dn,
            password=config.ldap_bind_pw,
            raise_exceptions=True,
            auto_bind=True,
        )

        search_attributes = [
            config.ldap_username_attribute,
            config.ldap_mail_attribute,
            config.ldap_display_name_attribute,
            config.ldap_groups_attribute,
        ]

        escaped_username = escape_filter_chars(username, "utf-8")

        connection.search(
            search_base=config.ldap_base_user_dn
            if config.ldap_base_user_dn is not None
            else config.ldap_base_dn,
            search_filter=config.ldap_user_search_filter.format(
                username=escaped_username
            ),
            attributes=search_attributes,
        )

        if not connection.entries:
            connection.unbind()
            raise UserNotFound()

        entry = connection.entries[0]
        connection.unbind()

        return {
            "username": entry[config.ldap_username_attribute].value
            if entry[config.ldap_username_attribute]
            else None,
            "groups": entry[config.ldap_groups_attribute].value
            if entry[config.ldap_groups_attribute]
            else [],
            "mail": entry[config.ldap_mail_attribute].value
            if entry[config.ldap_mail_attribute]
            else None,
            "display_name": entry[config.ldap_display_name_attribute].value
            if entry[config.ldap_display_name_attribute]
            else None,
        }
