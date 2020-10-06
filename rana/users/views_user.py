import logging
import uuid

from urllib import parse
import requests

from rana.common import code, urlmapper
from rana.common.http_utils import api_request_util, header_parser
from rana.common.models import ResultResponse
from rana.common.urlmapper import url_mapper
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


class UserInfo(APIView):
    def put(self, request):
        request_data = request.data
        result = ResultResponse(code.RANA_200_SUCCESS, 'success')
        try:
            print('request data for UserInfo:', str(request_data))
            open_id = request.META.get('HTTP_OPEN_ID')
            access_token = str(request.META['HTTP_AUTHORIZATION']).split(' ')[1]
            if 'is_active' in request_data or 'qualified' in request_data:
                logger_error.error('[Users][UserInfo][PUT]request data includes <is_active> or <qualified>')
                result = ResultResponse(code.RANA_401_UNAUTHORIZED, 'access to requested key is not allowed')
                return Response(result.get_response(), result.get_code())

            user_instance = User.objects.get(access_token=access_token, open_id=open_id)
        except Exception as e:
            print('UserInfo got error: ', str(e))
            logger_error.error(str(e))
            result = ResultResponse(code.RANA_401_UNAUTHORIZED, 'Token or user not found')
            return Response(result.get_response(), result.get_code())

        else:
            serializer = UserSerializer(user_instance, data=request_data, partial=True)
            if serializer.is_valid():
                user_login_info = UserLoginInfo.objects.get(user=user_instance)
                serializer.save()
                user_data = serializer.data
                user_data['login_key'] = user_login_info.login_key
                del user_data['id']

                result.set('user', user_data)
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
        logger_info.info('[Users][UserSingIn][Post]request data: {}'.format(str(request.data)))
        signin_manager = SignInManager(logger_info, logger_error)
        request_data = request.data
        result = ResultResponse(code.RANA_200_SUCCESS, 'success')
        try:
            login_key = request_data['login_key']
            login_value = request_data['login_value']
            user_data = signin_manager.set_login_data(login_key, login_value)
        except Exception as e:
            logger_info.info(str(e))
            resp_msg = {'message': 'invalid id and password'}
            result = ResultResponse(code.RANA_401_UNAUTHORIZED, 'invalid id and password')
            return Response(result.get_response(), result.get_code())
        else:
            print('user_data for signin: ', str(user_data))
            if user_data is not None:
                result.set('user', user_data)
            else:
                result = ResultResponse(code.RANA_401_UNAUTHORIZED, 'invalid id and password')
            return Response(result.get_response(), result.get_code())


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
        print('getting into user validation post...')
        request_data = request.data
        logger_info.info(request_data)

        result = ResultResponse(code.RANA_200_SUCCESS, 'success')

        try:
            access_token = request_data['access_token']
            open_id = request_data['open_id']
            user_qs = User.objects.filter(open_id=open_id, access_token=access_token)
        except Exception as e:
            logger_error.error(str(e))
            print('exception on user_validation: ', str(e))
            result = ResultResponse(code.RANA_401_UNAUTHORIZED, 'Error : ' + str(e))
            return Response(result.get_response(), result.get_code())

        try:
            user_count = user_qs.count()
            user = user_qs.get()
            user_logininfo = UserLoginInfo.objects.get(user=user)
            print(user_logininfo.login_key)
            user_serializer = UserSerializer(user)
            user_data = user_serializer.data
            user_data['login_key'] = user_logininfo.login_key
            del user_data['id']

            result.set('user', user_data)
        except Exception as e:
            print('exception on user serialization while_validation: ', str(e))
            logger_info.info(str(e))
            result = ResultResponse(code.RANA_400_BAD_REQUEST, 'Request data invalid')
            return Response(result.get_response(), result.get_code())

        if user_count < 1:
            logger_info.info('Request_data_invalid')
            result = ResultResponse(code.RANA_400_BAD_REQUEST, 'Request data invalid')
            return Response(result.get_response(), result.get_code())

        return Response(result.get_response(), result.get_code())


class UserExists(APIView):
    """
        GET allowed<br/>
        supports only application/json <br/>
        /users/id/<login_key> <br/>
        회원 가입 시 ID중복 여부를 확인
        """
    def get(self, request, login_key):
        result = ResultResponse(code.RANA_200_SUCCESS, 'success')

        try:
            signup_manager = SignUpManager(logger_info, logger_error)
            user_exists = signup_manager.check_user_exists(login_key)
        except Exception as e:
            result = ResultResponse(code.RANA_500_INTERNAL_SERVER_ERROR, str(e))
        else:
            result.set('is_exists', user_exists)

        return Response(result.get_response(), result.get_code())


class UserHandleBCFile(APIView):

    def post(self, request):
        result = ResultResponse(code.RANA_200_SUCCESS, 'success')
        try:
            auth_info = api_request_util.get_user_information_on_request(request)
            if not auth_info[0]:
                logger_info.info('[OssFile][POST]uploading file failed via unauthorized user')
                result = ResultResponse(code.RANA_401_UNAUTHORIZED, 'Unauthorized attempt')
                return Response(result.get_response(), result.get_code())
        except Exception as e:
            print(e)
            logger_info.info('[OssFile][POST]exception happens while uploading file')
            result = ResultResponse(code.RANA_401_UNAUTHORIZED, 'Unauthorized attempt')
            return Response(result.get_response(), result.get_code())

        if 'file' in request.FILES:
            try:
                print('request file: ', request.FILES['file'])
                auth_info = header_parser.parse_auth_info(request)
                open_id = auth_info.open_id
                access_token = auth_info.access_token

                query_dict = {
                    'target': 'user',
                    'object-id': open_id,
                    'media': 'businesscard'
                }
                query = parse.urlencode(query_dict, encoding='UTF-8')
                url = url_mapper.get('OSS_FILE_UPLOAD') + '?' + query
                headers = {'Authorization': 'bearer ' + access_token,
                           'open-id': open_id,
                           'content-type': 'multipart/form-data'}
                response = requests.post(url, headers=headers, files={'file': request.FILES['file']})
                if response.status_code == code.RANA_200_SUCCESS:
                    print('file upload: ', str(response))
                    response_json = response.json()
                    result.set('upload_filename', response_json['upload_filename'])
                    result.set('upload_file_ext', response_json['upload_file_ext'])
                else:
                    print('upload error:', str(response))
                    result = ResultResponse(code.RANA_500_INTERNAL_SERVER_ERROR, 'Cannot store file onto OSS server')

            except Exception as e:
                logger_error.error('[User][UserHandleBCFile]file upload failed')
                result = ResultResponse(code.RANA_500_INTERNAL_SERVER_ERROR, 'Cannot store file')
            else:
                logger_error.error('[User][UserHandleBCFile]No file is found')
                result = ResultResponse(code.RANA_400_BAD_REQUEST, 'No file is uploaded')
                print('no file!!')

            return Response(result.get_response(), result.get_code())
