from collections import namedtuple
from rana.common.exceptions.exceptions import AuthInfoError


def parse_auth_info(request):
    if request.META.get('HTTP_OPEN_ID'):
        open_id = request.META['HTTP_OPEN_ID']
    else:
        open_id = None

    if request.META.get('HTTP_AUTHORIZATION'):
        authorization = str(request.META['HTTP_AUTHORIZATION']).split(' ')
        if len(authorization) >= 2:
            access_token = authorization[1]
        else:
            access_token = None
    else:
        access_token = None

    AuthInfo = namedtuple("AuthInfo", 'open_id access_token')
    return AuthInfo(open_id=open_id, access_token=access_token)


def parse_auth_info_with_exception(request):
    if request.META.get('HTTP_OPEN_ID'):
        open_id = request.META['HTTP_OPEN_ID']
    else:
        open_id = None

    if request.META.get('HTTP_AUTHORIZATION'):
        authorization = str(request.META['HTTP_AUTHORIZATION']).split(' ')
        if len(authorization) >= 2:
            access_token = authorization[1]
        else:
            access_token = None
    else:
        access_token = None

    if open_id is None or access_token is None:
        raise AuthInfoError

    AuthInfo = namedtuple("AuthInfo", 'open_id access_token')
    return AuthInfo(open_id=open_id, access_token=access_token)