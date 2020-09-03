import binascii
import os

import logging
from rana.bplatform.models import AuthToken
from rana.bplatform.serializers import AuthTokenSerializer
from rest_framework.response import Response
from rest_framework.views import APIView

from rana.common import code
from rana.common.models import ResultResponse
from rana.users.models import User

logger_info = logging.getLogger('platform_info')
logger_error = logging.getLogger('platform_error')


class Token(APIView):
    """
    Handles token for user validation
    """
    def post(self, request):
        result = ResultResponse(code.RANA_200_SUCCESS, 'success')
        request_data = request.data
        logger_info.info(request_data)

        try:
            user_open_id = request_data['user_open_id']
            user_type = request_data['user_type']
            is_active = request_data['is_active']

        except Exception as e:
            logger_info.info(str(e))
            result = ResultResponse(code.RANA_400_BAD_REQUEST, 'Request data invalid')
            return Response(result.get_response(), result.get_code())

        # create platform & platform check
        while True:
            auth_token = binascii.hexlify(os.urandom(24)).decode()
            token_count = AuthToken.objects.filter(access_token=auth_token).count()

            if token_count == 0:
                break

        auth_token = auth_token.upper()
        request_data['access_token'] = auth_token
        request_data['user_type'] = user_type
        request_data['is_active'] = is_active

        prev_token_count = AuthToken.objects.filter(user_open_id=user_open_id).count()

        if prev_token_count == 1:
            prev_token = AuthToken.objects.get(user_open_id=user_open_id)
            prev_token.access_token = auth_token
            prev_token.save()
            result.set('token', auth_token)
        else:
            token_serializer = AuthTokenSerializer(data=request_data)

            if token_serializer.is_valid():
                token_serializer.save()
                result.set('token', auth_token)
            else:
                result = ResultResponse(code.RANA_400_BAD_REQUEST, 'Request data invalid')
                return Response(result.get_response(), result.get_code())

        return Response(result.get_response(), result.get_code())

    def put(self, request):
        result = ResultResponse(code.RANA_200_SUCCESS, 'success')
        request_data = request.data
        logger_info.info(request_data)

        try:
            user_open_id = request_data['user_open_id']
            auth_token = AuthToken.objects.get(user_open_id=user_open_id)
            if 'user_type' in request_data:
                auth_token.user_type = request_data['user_type']
            if 'is_active' in request_data:
                auth_token.is_active = request_data['is_active']

            auth_token.save()

            return Response(result.get_response(), result.get_code())

        except Exception as e:
            logger_info.info(str(e))
            result = ResultResponse(code.RANA_400_BAD_REQUEST, 'Request data invalid')
            return Response(result.get_response(), result.get_code())

    def delete(self, request):
        result = ResultResponse(code.RANA_200_SUCCESS, 'success')
        request_data = request.data
        logger_info.info(request_data)

        try:
            user_open_id = request_data['user_open_id']

            auth_token = AuthToken.objects.get(user_open_id=user_open_id)

            user = User.objects.get(open_id=user_open_id, access_token=auth_token.access_token)
            user.access_token = ''
            user.save()

            auth_token.delete()
        except Exception as e:
            logger_info.info(str(e))
            result = ResultResponse(code.RANA_400_BAD_REQUEST, 'Request data invalid')
            return Response(result.get_response(), result.get_code())

        return Response(result.get_response(), result.get_code())

