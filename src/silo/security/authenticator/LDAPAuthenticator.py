from ldap3 import Connection, Server, ALL
from ldap3.utils.conv import escape_filter_chars
from ldap3.core.exceptions import LDAPInvalidCredentialsResult

from silo.security.authenticator import BaseAuthenticator
from silo.security.authenticator.exceptions import InvalidCredentialsError


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

        self.server = Server(
            self.server_uri,
            use_ssl=self.use_ssl,
            get_info=ALL,
        )

    def authenticate(self, username: str, password: str) -> bool:

        escaped_username = escape_filter_chars(username, "utf-8")
        user_dn = self.user_dn_template.format(username=escaped_username)

        try:
            server_conn = Connection(
                self.server,
                user=user_dn,
                password=password,
                auto_bind=True,
                raise_exceptions=True,
            )
        except LDAPInvalidCredentialsResult:
            raise InvalidCredentialsError()

        return True
