import logging
import json
import uuid

from urllib import parse
import requests

from rana.common import code, urlmapper
from rana.common.exceptions.exceptions import DataValidationError
from rana.common.http_utils import api_request_util, header_parser
from rana.common.models import ResultResponse
from rana.portfolio.common import portfolio_func
from rana.portfolio.manager.portfolio_manager import PortfolioManager
from rest_framework.views import APIView
from rest_framework.response import Response

# Create your views here.
logger_info = logging.getLogger('portfolio_info')
logger_error = logging.getLogger('portfolio_error')


class PortfolioList(APIView):
    def get(self, request):
        result = ResultResponse(code.RANA_200_SUCCESS, 'success')
        query_str = request.GET.get('query', None)
        business_types_str = request.GET.get('business_type', None)
        page = request.GET.get('page', 1)
        limit = request.GET.get('limit', 30)
        portfolio_manager = PortfolioManager(logger_info, logger_error)
        if query_str is not None:
            print('query_str: {}, type: {}'.format(query_str, type(query_str)))
            try:
                query_list = json.loads(query_str)
                portfolios_data = portfolio_manager.read_portfolios_with_ids(page, limit, query_list)
                print('portfolios_data by ids', str(portfolios_data))
            except Exception as e:
                print('error: ', str(e))
            else:
                result.set('portfolios', portfolios_data)
        elif business_types_str is not None:
            print('business type list: ', business_types_str)
            try:
                business_type_list = json.loads(business_types_str)
                portfolios_data = portfolio_manager.read_portfolios_with_business_type(page, limit, business_type_list)
                print('portfolios_data by business type: ', str(portfolios_data))
            except Exception as e:
                print('error while business type list parsing:', str(e))
            else:
                result.set('portfolios', portfolios_data)
        else:
            try:
                portfolios_data = portfolio_manager.read_portfolios_with_business_type(page, limit)
                print('all portfolios_data: ', str(portfolios_data))
            except Exception as e:
                print('error while getting portfolios:', str(e))
            else:
                result.set('portfolios', portfolios_data)
        return Response(result.get_response(), result.get_code())

    def post(self, request):
        """
        Upload Contents file data
        Store new tag
        Store portfolio data -> Content data
            Update business_category as selected tags
        Update tag.portfolios on selected tags
        :param request:
        :return:
        """
        print('portfolio post')
        result = ResultResponse(code.RANA_200_SUCCESS, 'success')
        try:
            auth_info = api_request_util.validate_user_res_openid_on_request(request)
            if not auth_info[0]:
                logger_info.info('[PortfolioList][POST]Creating portfolio failed via unauthorized user')
                result = ResultResponse(code.RANA_401_UNAUTHORIZED, 'Unauthorized attempt')
                return Response(result.get_response(), result.get_code())
            if auth_info[2]['user_type'] != 2:
                result = ResultResponse(code.RANA_401_UNAUTHORIZED,
                                        'Only `start-up` user can create or change portfolio.')

            open_id = auth_info[1]
            request_data = request.data
            portfolio_data = request_data['portfolio']
            portfolio_content_data = portfolio_data['content']
            del portfolio_data['content']

            portfolio_manager = PortfolioManager(logger_info, logger_error)
            if len(portfolio_manager.read_my_portfolios(open_id)) > 0:
                raise DataValidationError
                #   only one portfolio is permitted per one user
            portfolio_response, updated_tag_data = portfolio_manager.create_my_portfolio(open_id, portfolio_data, portfolio_content_data)

            result.set('portfolio', portfolio_response)
            result.set('tags', updated_tag_data)
        except DataValidationError as dataError:
            result = ResultResponse(code.RANA_400_BAD_REQUEST, 'Already have a portfolio')
            print('Already have a portfolio')
        except Exception as e:
            result = ResultResponse(code.RANA_401_UNAUTHORIZED, 'Unauthorized attempt')
            print('Portfolio post error:', str(e))

        return Response(result.get_response(), result.get_code())


class PortfolioDetail(APIView):
    def get(self, request):
        result = ResultResponse(code.RANA_200_SUCCESS, 'success')
        try:
            auth_info = api_request_util.validate_user_res_openid_on_request(request)
            if not auth_info[0]:
                logger_info.info('[PortfolioList][POST]Creating portfolio failed via unauthorized user')
                result = ResultResponse(code.RANA_401_UNAUTHORIZED, 'Unauthorized attempt')
                return Response(result.get_response(), result.get_code())

            open_id = auth_info[1]
            portfolio_manager = PortfolioManager(logger_info, logger_error)
            portfolio_datas = portfolio_manager.read_my_portfolios(open_id)
            result.set('portfolio', portfolio_datas[0])
        except Exception as e:
            result = ResultResponse(code.RANA_401_UNAUTHORIZED, 'Unauthorized attempt')
        # portfolio_manager = PortfolioManager(logger_info, logger_error)
        return Response(result.get_response(), result.get_code())

    def put(self, request):
        result = ResultResponse(code.RANA_200_SUCCESS, 'success')
        try:
            auth_info = api_request_util.validate_user_res_openid_on_request(request)
            if not auth_info[0]:
                logger_info.info('[PortfolioList][POST]Creating portfolio failed via unauthorized user')
                result = ResultResponse(code.RANA_401_UNAUTHORIZED, 'Unauthorized attempt')
                return Response(result.get_response(), result.get_code())
            if auth_info[2]['user_type'] != 2:
                result = ResultResponse(code.RANA_401_UNAUTHORIZED, 'Only `start-up` user can create or change portfolio.')
            print('user response:', str(auth_info[2]))
            print('user_type', auth_info[2]['user_type'])
            open_id = auth_info[1]
            request_data = request.data
            portfolio_data = request_data['portfolio']
            portfolio_func.portfolio_put_validation(portfolio_data, open_id)

            portfolio_content_data = portfolio_data['content']
            del portfolio_data['content']

            portfolio_manager = PortfolioManager(logger_info, logger_error)
            portfolio_res_data, updated_tag_data = portfolio_manager.update_my_portfolio(open_id, portfolio_data['id'], portfolio_data, portfolio_content_data)

            result.set('portfolio', portfolio_res_data)
            result.set('tags', updated_tag_data)
        except DataValidationError as dataError:
            message, err_code = dataError.args
            result = ResultResponse(code.RANA_400_BAD_REQUEST, message, err_code)
        except Exception as e:
            print('Put my portfolio error:', str(e))
            result = ResultResponse(code.RANA_401_UNAUTHORIZED, 'Unauthorized attempt')
        return Response(result.get_response(), result.get_code())


class PortfolioInfo(APIView):
    """
    GET allowed<br/>
    Get detail data of requested portfolio
    /portfolio/<portfolio_id> <br/>
    portfolio 의 상세 내용을 기술하는 정보를 가져온다
    """
    def get(self, request, portfolio_id):
        result = ResultResponse(code.RANA_200_SUCCESS, 'success')
        try:
            auth_info = api_request_util.validate_user_res_openid_on_request(request)
            if not auth_info[0]:
                logger_info.info('[PortfolioList][POST]Creating portfolio failed via unauthorized user')
                result = ResultResponse(code.RANA_401_UNAUTHORIZED, 'Unauthorized attempt')
                return Response(result.get_response(), result.get_code())
            user_type = auth_info[2]['user_type']
            portfolio_manager = PortfolioManager(logger_info, logger_error)
            portfolio_data = portfolio_manager.read_portfolio(portfolio_id, user_type)
            if portfolio_data is None:
                logger_info.info('[PortfolioList][{}][GET]No such portfolio exists or accessible'.
                                 format(str(portfolio_id)))
                result = ResultResponse(code.RANA_404_NOT_FOUND, 'No such portfolio exists')
            else:
                result.set('portfolio', portfolio_data)
            locale = request.GET.get('locale', 'ko')
            tag_data = portfolio_manager.read_tag_list(locale, portfolio_data['business_category'])
            result.set('tags', tag_data)
        except Exception as e:
            print('Error while getting pf detail:', str(e))
            result = ResultResponse(code.RANA_401_UNAUTHORIZED, 'Unauthorized attempt')
        return Response(result.get_response(), result.get_code())


class TagInfo(APIView):
    def get(self, request):
        result = ResultResponse(code.RANA_200_SUCCESS, 'success')
        try:
            portfolio_manager = PortfolioManager(logger_info, logger_error)
            locale = request.GET.get('locale', 'ko')
            tag_data = portfolio_manager.read_tag_list(locale)
        except Exception as e:
            print(str(e))
            message, err_code = e.args
            result = ResultResponse(code.RANA_400_BAD_REQUEST, message, err_code)
        else:
            result.set('tags', tag_data)
        return Response(result.get_response(), result.get_code())

    def post(self, request):
        """
        Adding tag is independent from handling portfolio objects
        User can add unlimited tags onto server on the cases:
        1. create portfolio, 2. modify portfolio. But all the newly
        added terms will be hidden without authorization by admin.
        :param request:
        {
            'portfolio_id' : <target portfolio id>
            'tag_term' : { 'locale' : <locale string, default=ko>,
                    'term' : <Tag term> }
        }
        :return:
        """
        result = ResultResponse(code.RANA_200_SUCCESS, 'success')
        try:
            auth_info = api_request_util.validate_user_res_openid_on_request(request)
            if not auth_info[0]:
                logger_info.info('[PortfolioList][POST]Creating portfolio failed via unauthorized user')
                result = ResultResponse(code.RANA_401_UNAUTHORIZED, 'Unauthorized attempt')
                return Response(result.get_response(), result.get_code())
            portfolio_manager = PortfolioManager(logger_info, logger_error)
            request_data = request.data
            print('request_data:', str(request_data))
            portfolio_id = request_data.get('portfolio_id', None)
            # tag_term_data = request_data['tag_term']
            locale = request_data.get('locale', 'ko')
            term = request_data.get('term', None)
            # tag_data_result = portfolio_manager.create_tag(tag_term_data, portfolio_id)
            tag_data_result = portfolio_manager.get_or_create_tag(locale, term, portfolio_id)
        except Exception as e:
            print(str(e))
            message, err_code = e.args
            result = ResultResponse(code.RANA_400_BAD_REQUEST, message, err_code)
        else:
            result.set('tags', tag_data_result)
        return Response(result.get_response(), result.get_code())

    def put(self, request):
        result = ResultResponse(code.RANA_200_SUCCESS, 'success')
        try:
            request_data = request.data
            target_tag_list = request_data['tag_list']
            target_portfolio_id = request_data['portfolio_id']
            portfolio_manager = PortfolioManager(logger_info, logger_error)
            tag_list = portfolio_manager.update_tag_with_portfolio(target_tag_list, target_portfolio_id)
        except Exception as e:
            print(str(e))
            message, err_code = e.args
            result = ResultResponse(code.RANA_400_BAD_REQUEST, message, err_code)
        else:
            result.set('tag_list', tag_list)
        return Response(result.get_response(), result.get_code())


class TagSearch(APIView):
    def get(self, request):
        result = ResultResponse(code.RANA_200_SUCCESS, 'success')
        try:
            portfolio_manager = PortfolioManager(logger_info, logger_error)
            locale = request.GET.get('locale', 'ko')
            term = request.GET.get('term', None)
            if term is not None:
                tag_data = portfolio_manager.get_or_create_tag(locale, term)
            else:
                tag_data = []
        except Exception as e:
            print(str(e))
            message, err_code = e.args
            result = ResultResponse(code.RANA_400_BAD_REQUEST, message, err_code)
        else:
            result.set('tags', tag_data)
        return Response(result.get_response(), result.get_code())