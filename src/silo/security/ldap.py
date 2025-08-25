from ldap3 import Server, Connection, ALL
from ldap3.core.exceptions import LDAPBindError, LDAPException

from silo import config
from silo.log import logger


def ldap_authenticate(username: str, password: str):

    server = Server(config.ldap_server_uri, get_info=ALL)
    user_dn = config.ldap_user_dn_template.format(username=username)

    try:
        try:
            conn = Connection(server, user=user_dn, password=password, auto_bind=True)
        except Exception as e:
            return False

        conn.unbind()
        return True
    except Exception as e:
        logger.error("LDAP ERROR: ", exc_info=True)
        return False
