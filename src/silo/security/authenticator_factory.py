from silo import config
from silo.security import authenticator


def create_authenticator() -> authenticator.BaseAuthenticator:
    auth_class = config.authenticator_class

    match auth_class:

        # LDAPAuthenticator
        case authenticator.LDAPAuthenticator:
            return auth_class(
                server_uri=config.ldap_server_uri,
                user_dn_template=config.ldap_user_dn_template,
                base_dn=config.ldap_base_dn,
                allowed_groups=config.ldap_allowed_groups,
                use_ssl=config.ldap_use_ssl,
                ssl_skip_verify=config.ldap_ssl_skip_verify,
                bind_dn=config.ldap_bind_dn,
                bind_pw=config.ldap_bind_pw,
            )

        case _:
            return auth_class()
