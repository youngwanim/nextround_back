import logging
import json

from rana.common import code, urlmapper
from rana.common.exceptions.exceptions import DataValidationError
from rana.common.http_utils import api_request_util, header_parser
from rana.common.models import ResultResponse
from rana.event.manager.event_manager import EventManager
from rest_framework.views import APIView
from rest_framework.response import Response

# Create your views here.
logger_info = logging.getLogger('event_info')
logger_error = logging.getLogger('event_error')


class EventList(APIView):
    def get(self, request):
        pass


class EventInfo()
