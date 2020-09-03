import logging
import uuid

import requests

from rana.common import code, urlmapper
from rana.common.models import ResultResponse
from rana.users.manager.sign_in_manager import SignInManager
from rana.users.manager.sign_up_manager import SignUpManager
from rana.users.models import User, UserLoginInfo
from rana.users.serializers import UserSerializer, UserLoginInfoSerializer
from django.http import Http404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

logger_info = logging.getLogger('users_info')
logger_error = logging.getLogger('users_error')


class UserList(APIView):

    def get(self, request, format=None):
        users = User.objects.all()
        print('users=', users)
        serializer = UserSerializer(users, many=True)
        print('user serializer= ', serializer.data)
        return Response(serializer.data)

    def post(self, request, ):
        request_data = request.data
        serializer = UserSerializer(data=request_data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserLoginInfoDetail(APIView):
    def get(self, request, open_id):
        try:
            user_obj = User.objects.get(open_id=open_id)
        except User.DoesNotExist:
            raise Http404
        try:
            user_login_info_obj = UserLoginInfo.objects.get(user=user_obj)
            user_login_info_serializer = UserLoginInfoSerializer(user_login_info_obj)
        except UserLoginInfo.DoesNotExist:
            raise Http404

        return Response(user_login_info_serializer.data)


class User(APIView):
    def put(self, request, open_id):
        request_data = request.data
        result = ResultResponse(code.RANA_200_SUCCESS, 'success')

        try:
            access_token = str(request.META['HTTP_AUTHORIZATION']).split(' ')[1]
            user_instance = User.objects.get(access_token=access_token, open_id=open_id)
        except Exception as e:
            logger_error.error(str(e))
            result = ResultResponse(code.RANA_401_UNAUTHORIZED, 'Token or user not found')
            return Response(result.get_response(), result.get_code())

        else:
            serializer = UserSerializer(user_instance, data=request_data, partial=True)
            if serializer.is_valid():
                serializer.save()
            else:
                logger_error.error(serializer.errors)
                result = ResultResponse(code.RANA_401_UNAUTHORIZED, 'Token or user not found')
                return Response(result.get_response(), result.get_code())

            return Response(result.get_response(), result.get_code())


class UserSignIn(APIView):
    """
    POST allowed<br/>
    supports only application/json <br/>
    /users/signin <br/>
    ID와 비밀번호로 로그인 시 사용하는 API
    body 예: {"login_key": "CUSTOMER_ID", "login_value":"CUSTOMER_PASSWORD"
    """

    def post(self, request):
        logger_info.info(request.data)
        signin_manager = SignInManager(logger_info, logger_error)
        request_data = request.data
        print(str(request_data))
        try:
            login_key = request_data['login_key']
            login_value = request_data['login_value']
            user_data = signin_manager.set_login_data(login_key, login_value)
        except Exception as e:
            logger_info.info(str(e))
            resp_msg = {'message': 'invalid id and password'}
            return Response(resp_msg, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(user_data, status=status.HTTP_200_OK)


class UserSignUp(APIView):
    """
    POST allowed<br/>
    supports only application/json <br/>
    /users/signup <br/>
    회원 가입 시 사
    """
    def post(self, request):
        result = ResultResponse(code.RANA_200_SUCCESS, 'success')
        signup_manager = SignUpManager(logger_info, logger_error)
        try:
            # create open id
            random_token = str(uuid.uuid4()).split('-')
            open_id = str(random_token[0] + random_token[2] + random_token[4]).upper()

            request_data = request.data
            request_data['open_id'] = open_id

            payload = {'user_open_id': open_id,
                       'user_type': request_data['user_type'],
                       'is_active': False
                       }
            response = requests.post(urlmapper.get_url('TOKEN'), json=payload)
            if response.status_code == code.RANA_200_SUCCESS:
                response_json = response.json()
                token = response_json['token']
                request_data['token'] = str(token).upper()
                request_data['open_id'] = open_id
                print(request_data)
                user_data = signup_manager.set_user_data(request_data)
                result.set('user', user_data)
            else:
                result = ResultResponse(code.RANA_500_INTERNAL_SERVER_ERROR, 'API connection failed')
                result.set_error(code.ERROR_9000_INTERNAL_API_CALL_FAILED)
                logger_error.error(response.text)

        except Exception as e:
            logger_info.info(str(e))
            result = ResultResponse(code.RANA_400_BAD_REQUEST, 'Request data is invalid')

        return Response(result.get_response(), result.get_code())


class UserValidation(APIView):

    def post(self, request):
        request_data = request.data
        logger_info.info(request_data)

        result = ResultResponse(code.RANA_200_SUCCESS, 'success')

        try:
            access_token = request_data['access_token']
            open_id = request_data['open_id']
            user_qs = User.objects.filter(open_id=open_id, access_token=access_token)
        except Exception as e:
            logger_error.error(str(e))
            result = ResultResponse(code.RANA_401_UNAUTHORIZED, 'Error : ' + str(e))
            return Response(result.get_response(), result.get_code())

        try:
            user_count = user_qs.count()
            user = user_qs.get()

            user_serializer = UserSerializer(user)
            user_data = user_serializer.data

            result.set('user', user_data)
        except Exception as e:
            logger_info.info(str(e))
            result = ResultResponse(code.RANA_400_BAD_REQUEST, 'Request data invalid')
            return Response(result.get_response(), result.get_code())

        if user_count < 1:
            logger_info.info('Request_data_invalid')
            result = ResultResponse(code.RANA_400_BAD_REQUEST, 'Request data invalid')
            return Response(result.get_response(), result.get_code())

        return Response(result.get_response(), result.get_code())