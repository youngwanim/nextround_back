import uuid
import os
import logging

from django.conf import settings
from django.core.files.storage import FileSystemStorage
from rest_framework.response import Response
from rest_framework.views import APIView

from rana.common import code
from rana.common.http_utils import api_request_util
from rana.common.models import ResultResponse

logger_info = logging.getLogger('oss_info')
logger_error = logging.getLogger('oss_error')


class OssFile(APIView):
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

        print('request: ', str(request))

        if 'file' in request.FILES:
            try:
                # File object create
                print('oss request: ', str(request))
                target = request.GET.get('target', None)
                object_id = request.GET.get('object-id', None)
                media = request.GET.get('media', None)
                if target is not None:
                    if not os.path.isdir(target):
                        os.mkdir(target)
                    if object_id is not None:
                        if not os.path.isdir(target + '/' + object_id):
                            os.mkdir(target + '/' + object_id)
                        if media is not None:
                            if not os.path.isdir(target + '/' + object_id + '/' + media):
                                os.mkdir(target + '/' + object_id + '/' + media)

                file = request.FILES['file']
                fs = FileSystemStorage()
                filename = target + '/' + object_id + '/' + media + '/' + self.make_file_name(file.name)
                upload_filename = fs.save(filename, file)
                upload_file_ext = filename.split('.')[-1]
                print(upload_filename)
                # fs.delete(filename)
                #
                if settings.DEBUG:
                    upload_filename = '/media/' + upload_filename

                result.set('upload_filename', upload_filename)
                result.set('upload_file_ext', upload_file_ext)

            except Exception as e:
                print('[Oss][Upload]file upload failed by: ', str(e))
                logger_error.error('[Oss][Upload]file upload failed by: ', str(e))
                result = ResultResponse(code.RANA_500_INTERNAL_SERVER_ERROR, 'Cannot store file')
        elif 'files' in request.FILES:
            try:
                # File object create
                print('oss request: ', str(request))
                target = request.GET.get('target', None)
                object_id = request.GET.get('object-id', None)
                media = request.GET.get('media', None)
                if target is not None:
                    if not os.path.isdir(target):
                        os.mkdir(target)
                    if object_id is not None:
                        if not os.path.isdir(target + '/' + object_id):
                            os.mkdir(target + '/' + object_id)
                        if media is not None:
                            if not os.path.isdir(target + '/' + object_id + '/' + media):
                                os.mkdir(target + '/' + object_id + '/' + media)

                # files = request.FILES['files']
                # fileItems = request.FILES.items()
                print('request files:', str(request.FILES.getlist('files')))
                files = request.FILES.getlist('files')
                print('files:', files)
                fs = FileSystemStorage()
                upload_filename = list()
                upload_file_ext = list()
                for i, file in enumerate(files):
                    filename = target + '/' + object_id + '/' + media + '/' + self.make_file_name(file.name)
                    single_filename = fs.save(filename, file)
                    upload_file_ext.append(filename.split('.')[-1])

                    if settings.DEBUG:
                        upload_filename.append('/media/' + single_filename)
                print(upload_filename)
                result.set('upload_filename', upload_filename)
                result.set('upload_file_ext', upload_file_ext)

            except Exception as e:
                print('[Oss][Upload]file upload failed by: ', str(e))
                logger_error.error('[Oss][Upload]file upload failed by: ', str(e))
                result = ResultResponse(code.RANA_500_INTERNAL_SERVER_ERROR, 'Cannot store file')
        else:
            print('request files:', str(request.FILES))
            logger_error.error('[Oss][Upload]No file is found')
            result = ResultResponse(code.RANA_400_BAD_REQUEST, 'No file is uploaded')
            print('no file!!')

        return Response(result.get_response(), result.get_code())

    def make_file_name(self, filename):
        random_str = str(uuid.uuid4()).replace('-', '')[:6]
        return filename.split('.')[0] + '-' + random_str + '.' + filename.split('.')[-1]

    def delete(self, request):
        print(request.data)

