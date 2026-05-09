import ldap
from config import LDAP_URI, BIND_DN, BIND_PASS


def get_connection():
    ldap.set_option(ldap.OPT_X_TLS_REQUIRE_CERT, ldap.OPT_X_TLS_NEVER)
    conn = ldap.initialize(LDAP_URI)
    conn.set_option(ldap.OPT_REFERRALS, 0)
    conn.set_option(ldap.OPT_PROTOCOL_VERSION, ldap.VERSION3)
    conn.set_option(ldap.OPT_X_TLS_NEWCTX, 0)
    conn.start_tls_s()
    conn.simple_bind_s(BIND_DN, BIND_PASS)
    return conn
