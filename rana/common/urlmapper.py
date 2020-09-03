from django.conf import settings

if settings.DEBUG:
    HOST = 'http://localhost:8010'
    HOST_BPLATFORM = 'http://localhost:8010'
    HOST_USER = 'http://localhost:8010'
    HOST_PORTFOLIO = 'http://localhost:8010'
else:
    HOST = 'http://localhost:8010'
    HOST_BPLATFORM = 'http://localhost:8010'
    HOST_USER = 'http://localhost:8010'
    HOST_PORTFOLIO = 'http://localhost:8010'

url_mapper = dict()

# User
url_mapper['USER_INFO'] = HOST_USER + '/users'
url_mapper['USER_VALIDATION'] = HOST_USER + '/users/validation'
# Platform
url_mapper['TOKEN'] = HOST_BPLATFORM + '/platform/token'


def get_url(url_domain):
    return url_mapper.get(url_domain)
