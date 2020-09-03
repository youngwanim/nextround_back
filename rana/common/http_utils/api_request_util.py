import requests

from rana.common import code
from rana.common import urlmapper
from rana.common.exceptions.exceptions import AuthInfoError
from rana.common.http_utils.header_parser import parse_auth_info_with_exception


def get_user_information(open_id, access_token):
    payload = {'open_id': open_id, 'access_token': access_token}
    url = urlmapper.get_url('USER_VALIDATION')

    response = requests.post(url, json=payload)

    if response.status_code == code.RANA_200_SUCCESS:
        response_json = response.json()
        result = (True, response_json)
    else:
        result = (False, None)

    return result


def get_user_information_on_request(request):
    try:
        auth_info = parse_auth_info_with_exception(request)
        result = get_user_information(auth_info.open_id, auth_info.access_token)
    except AuthInfoError:
        result = (False, None)

    return result
