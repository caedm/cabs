import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))

TEMPLATE_DEBUG = False
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler'
        },
        'stream_to_console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler'
        },
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
        'django_auth_ldap': {
            'handlers': ['stream_to_console'],
            'level': 'DEBUG',
            'propagate': True,
        },
    }
}

SESSION_COOKIE_SECURE = True
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
CSRF_COOKIE_SECURE = True

# Django-auth-ldap
AUTHENTICATION_BACKENDS = (
    'django_auth_ldap.backend.LDAPBackend',
)

import ldap
from django_auth_ldap.config import LDAPSearch, MemberDNGroupType
#LDAP over TLS
AUTH_LDAP_GLOBAL_OPTIONS = {
    ldap.OPT_X_TLS_CACERTFILE: "/var/www/CABS_interface/caedm_ad.pem",
    ldap.OPT_X_TLS_REQUIRE_CERT: ldap.OPT_X_TLS_DEMAND,
}
AUTH_LDAP_START_TLS = True

AUTH_LDAP_USER_DN_TEMPLATE = "CAEDM_AD\\%(user)s"
AUTH_LDAP_BIND_AS_AUTHENTICATING_USER = True

#Find AUTO Auth Server
def findServer(domain):
    import dns.resolver
    domain = domain.replace('AUTO', '', 1)
    domain = domain.replace('ldap://', '')
    domain = domain.replace('ldaps://','')
    domain = '_ldap._tcp' + domain
    resolver = dns.resolver.Resolver()
    result = resolver.query(domain, 'SRV')
    server = result[0].target.to_text().strip('.')
    if not server.startswith("ldap://") and not server.startswith("ldaps://"):
        server = "ldap://" + server
    return server

AUTH_LDAP_SERVER_URI = findServer("AUTO.et.byu.edu")

AUTH_LDAP_CONNECTION_OPTIONS = {
    ldap.OPT_DEBUG_LEVEL: 1,
    ldap.OPT_REFERRALS: 0,
}

AUTH_LDAP_USER_SEARCH = LDAPSearch("dc=et,dc=byu,dc=edu", ldap.SCOPE_SUBTREE, "(cn=%(user)s)")

AUTH_LDAP_GROUP_TYPE = MemberDNGroupType('member')
AUTH_LDAP_GROUP_SEARCH = LDAPSearch('dc=et,dc=byu,dc=edu', ldap.SCOPE_SUBTREE)
#AUTH_LDAP_REQUIRE_GROUP = "cn=caedm_admin_level1,ou=caedm groups,ou=security groups,ou=caedm,ou=departments,dc=et,dc=byu,dc=edu"
AUTH_LDAP_MIRROR_GROUPS = True

CABS_LDAP_CAN_EDIT_GROUPS = [ 
    "Domain Admins",
]
CABS_LDAP_CAN_DISABLE_GROUPS = [ 
    "caedm_admin_level2",
    "caedm_admin_level3",
    "caedm_admin_level4",
    "caedm_admin_level5",
]
CABS_LDAP_CAN_VIEW_GROUPS = [ 
    "caedm_admin_level1",
]

LOGIN_URL = "cabs_admin:index"
LOGIN_REDIRECT_URL = 'cabs_admin:index'

# Application definition

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'cabs_admin'
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'admin_tools.urls'

WSGI_APPLICATION = 'admin_tools.wsgi.application'

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.core.context_processors.request',
)


# Internationalization
# https://docs.djangoproject.com/en/1.7/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.7/howto/static-files/

STATIC_ROOT = '/var/www/CABS_interface/static/'
STATIC_URL = '/static/'
STATICFILES_DIRS = [
        'cabs_admin/static',
        '/opt/cabsgraph/static'
]

#A patch to make django-auth-ldap work with Active Directory with direct bind
import django
# I think I had to add this line because the website wouldn't install without it. I don't think settings.py
# on cabs.et.byu.edu has this line.
django.setup()

from django_auth_ldap import backend

def monkey(self, password):
    if self.dn is None:
        raise self.AuthenticationFailed("failed to map the username to a DN.")
    try:
        sticky = self.settings.BIND_AS_AUTHENTICATING_USER
        self._bind_as(self.dn, password, sticky=sticky)
        #MonkeyPatch:
        if sticky and self.settings.USER_SEARCH:
            self._search_for_user_dn()
        #Patched
    except ldap.INVALID_CREDENTIALS:
        raise self.AuthenticationFailed("user DN/password rejected by LDAP server.")

backend._LDAPUser._authenticate_user_dn = monkey

AGGREGATE_GRAPHS = ["All_pools"]
GRAPH_LENGTHS = ["12h", "1d", "7d", "1M", "1y", "3y"]

try:
    from local_settings import *
except ImportError as e:
    pass
