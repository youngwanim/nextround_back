import uuid

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

        if 'file' in request.FILES:
            try:
                # File object create
                file = request.FILES['file']
                fs = FileSystemStorage()
                filename = self.make_file_name(file.name)
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
                logger_error.error('[Oss][Upload]file upload failed')
                result = ResultResponse(code.RANA_500_INTERNAL_SERVER_ERROR, 'Cannot store file')
        else:
            logger_error.error('[Oss][Upload]No file is found')
            result = ResultResponse(code.RANA_400_BAD_REQUEST, 'No file is uploaded')
            print('no file!!')

        return Response(result.get_response(), result.get_code())

    def make_file_name(self, filename):
        random_str = str(uuid.uuid4()).replace('-', '')[:6]
        return filename.split('.')[0] + '-' + random_str + '.' + filename.split('.')[-1]

    def delete(self, request):
        print(request.data)

