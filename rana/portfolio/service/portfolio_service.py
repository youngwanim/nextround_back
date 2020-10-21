import json

from django.core.paginator import Paginator
from django.db import transaction

from rana.common.exceptions.exceptions import BusinessLogicError, DataValidationError
from rana.portfolio.models import Portfolio, PortfolioContent, Tag, TagTerm
from rana.portfolio.serializers import PortfolioSerializer, PortfolioContentSerializer, \
    PortfolioContentListSerializer, TagSerializer, TagTermListSerializer, TagTermSerializer, TagWithTermSerializer


def check_auth_type(user_type, portfolio_data):
    portfolio_content_data = portfolio_data['content']
    if portfolio_content_data['auth_type'] < user_type:
        portfolio_data.pop('content', None)
    if portfolio_content_data['product_auth_type'] < user_type:
        portfolio_content_data.pop('product_title', None)
        portfolio_content_data.pop('product_sub_title', None)
        portfolio_content_data.pop('product_image_list', None)
        portfolio_content_data.pop('product_introduce', None)
    if portfolio_content_data['team_auth_type'] < user_type:
        portfolio_content_data.pop('team_title', None)
        portfolio_content_data.pop('team_sub_title', None)
        portfolio_content_data.pop('team_image_list', None)
        portfolio_content_data.pop('team_introduce', None)
    if portfolio_content_data['ceo_auth_type'] < user_type:
        portfolio_content_data.pop('ceo', None)
        portfolio_content_data.pop('ceo_sub_title', None)
        portfolio_content_data.pop('ceo_image_list', None)
        portfolio_content_data.pop('ceo_introduce', None)
    if portfolio_content_data['ir_auth_type'] < user_type:
        portfolio_content_data.pop('ir_file', None)

    return portfolio_data


class PortfolioService:

    def __init__(self, logger_info, logger_error):
        self.result = None
        self.logger_info = logger_info
        self.logger_error = logger_error

    def get_my_portfolio_list(self, open_id):
        try:
            portfolio_qs = Portfolio.objects.filter(open_id=open_id)
            portfolio_data = PortfolioSerializer(portfolio_qs, many=True).data
        except Exception as e:
            self.logger_error.error(str(e))
        else:
            self.result = portfolio_data

        return self.result

    def get_my_portfolio_business_category(self, portfolio_id):
        try:
            portfolio_inst = Portfolio.objects.get(id=portfolio_id)
            business_category = json.loads(portfolio_inst.business_category)
        except Exception as e:
            self.logger_error.error(str(e))
        else:
            self.result = business_category
        return self.result

    def get_my_portfolio_detail(self, portfolio_id):
        try:
            portfolio_content_inst = PortfolioContent.objects.get(portfolio=portfolio_id)
            portfolio_content_data = PortfolioContentSerializer(portfolio_content_inst).data
        except Exception as e:
            self.logger_error.error(str(e))
        else:
            self.result = portfolio_content_data

        return self.result

    def set_my_portfolio_detail(self, open_id, portfolio_id, portfolio_data, portfolio_content_data):
        try:
            portfolio_inst = Portfolio.objects.get(id=portfolio_id, open_id=open_id)
            portfolio_content_inst = PortfolioContent.objects.get(portfolio=portfolio_inst)

            # check business_category exists and it is valid

            with transaction.atomic():
                portfolio_serializer = PortfolioSerializer(portfolio_inst, data=portfolio_data, partial=True)
                portfolio_content_serializer = PortfolioContentSerializer(portfolio_content_inst,
                                                                          data=portfolio_content_data, partial=True)
                if portfolio_serializer.is_valid():
                    portfolio_serializer.save()
                if portfolio_content_serializer.is_valid():
                    portfolio_content_serializer.save()
        except Exception as e:
            self.logger_error.error(str(e))
        else:
            portfolio_res_data = portfolio_serializer.data
            portfolio_res_data['content'] = portfolio_content_serializer.data
            self.result = portfolio_res_data

        return self.result

    def set_my_portfolio_with_tag_ids(self, open_id, portfolio_id, tag_list):
        try:
            portfolio_inst = Portfolio.objects.get(id=portfolio_id, open_id=open_id)
            portfolio_content_inst = PortfolioContent.objects.get(portfolio=portfolio_inst)

            tag_ids = [tag['id'] for tag in tag_list]
            portfolio_inst.business_category = json.dumps(tag_ids)
            portfolio_inst.save()
            portfolio_data = PortfolioSerializer(portfolio_inst).data
            portfolio_content_data = PortfolioContentSerializer(portfolio_content_inst).data
            del portfolio_data['open_id']
            portfolio_data['content'] = portfolio_content_data
        except Exception as e:
            self.logger_error.error(str(e))
        else:
            self.result = {
                'portfolio': portfolio_data
            }
        return self.result

    def create_my_portfolio_detail(self, open_id, portfolio_data, portfolio_content_data):
        try:
            # if not self.validate_tag_ids(portfolio_data.get('business_category', [])):
            #     msg = '[portfolio_service][create_my_portfolio_detail]Wrong tag ids'
            #     print(msg)
            #     raise DataValidationError(msg, None, None)
            print('portfolio_data')
            with transaction.atomic():
                portfolio_data['open_id'] = open_id
                print('portfolio_data:', str(portfolio_data))
                portfolio_instance = Portfolio.objects.create(**portfolio_data)
                portfolio_content_data['portfolio'] = portfolio_instance
                print('portfolio_content_data:', str(portfolio_content_data))

                portfolio_content_instance = PortfolioContent.objects.create(**portfolio_content_data)
        except Exception as e:
            print('create_my_portfolio_detail exception happens')
            print('like:', str(e))
            self.logger_error.error(str(e))
            raise DataValidationError(str(e), None, None)
        else:
            portfolio_res_data = PortfolioSerializer(portfolio_instance).data
            del portfolio_res_data['open_id']
            portfolio_content_res_data = PortfolioContentSerializer(portfolio_content_instance).data
            portfolio_res_data['content'] = portfolio_content_res_data

            self.result = portfolio_res_data

        return self.result

    def get_portfolio_list_by_ids(self, page, limit, portfolio_ids=None):
        # for event or something
        # portfolio_qs = Portfolio.objects.filter(pk__in=portfolio_ids).select_related('content')
        portfolio_query = {'portfolio__is_activated': True}
        if portfolio_ids is not None:
            portfolio_query['portfolio__pk__in'] = portfolio_ids

        portfolio_content_qs = PortfolioContent.objects.filter(**portfolio_query).select_related('portfolio')
        paginator = Paginator(portfolio_content_qs, limit)
        portfolio_contents_paginator = paginator.get_page(page)
        portfolio_content_data = PortfolioContentListSerializer(portfolio_contents_paginator, many=True).data
        self.result = portfolio_content_data

        return self.result

    def get_portfolio_list(self, page, limit, business_type_list=None):
        # for gallery
        if business_type_list is not None:
            tag_qs = Tag.objects.filter(term__in=business_type_list)
            tag_list = TagSerializer(tag_qs, many=True).data
            portfolio_ids_set = set()
            for i, tag in enumerate(tag_list):
                portfolio_ids_set = portfolio_ids_set | set(json.loads(tag['portfolios']))
            print(str(portfolio_ids_set))
            portfolio_list = self.get_portfolio_list_by_ids(page, limit, list(portfolio_ids_set))
        else:
            portfolio_list = self.get_portfolio_list_by_ids(page, limit)

        self.result = portfolio_list
        return self.result

    def get_portfolio_detail(self, portfolio_id, user_type):
        # for detail : if auth_type of target portfolio is bigger than user_type
        try:
            portfolio_inst = Portfolio.objects.get(id=portfolio_id)
            portfolio_data = PortfolioSerializer(portfolio_inst).data
            if portfolio_data['is_activated']:
                portfolio_content_inst = PortfolioContent.objects.get(portfolio=portfolio_inst)
                portfolio_content_data = PortfolioContentSerializer(portfolio_content_inst).data
                portfolio_data['content'] = portfolio_content_data
                portfolio_data = check_auth_type(user_type, portfolio_data)
                print('portfolio_data by user_type: ', str(portfolio_data))
            else:
                self.logger_info.info('Portfolio ID({}) is not activated yet'.format(portfolio_id))
                self.result = None
        except Exception as e:
            self.logger_error.error(str(e))
        else:
            self.result = portfolio_data

        return self.result

    def check_tag_term_exist(self, term, locale):
        term_exist = TagTerm.objects.filter(term=term, locale=locale).exists()
        self.result = term_exist
        print('result of check_tag_term_exist:{}, with term: {}'.format(self.result, term))
        return self.result

    def create_tag(self, tag_term, portfolio_id=None):
        try:
            tag_data = dict()
            tag_data['code'] = tag_term['term']
            tag_data['is_activated'] = False

            if portfolio_id is not None:
                tag_data['portfolios'] = json.dumps([portfolio_id])

            with transaction.atomic():
                tag_inst = Tag.objects.create(**tag_data)
                tag_term['tag'] = tag_inst.id
                tag_term_serializer = TagTermSerializer(data=tag_term)
                if tag_term_serializer.is_valid():
                    tag_term_serializer.save()
                else:
                    print('tag term data is not valid', str(tag_term))
                    msg = 'input tag term is not valid'
                    self.logger_error.error(msg)
                    raise DataValidationError(msg, None, None)

            tag_data = TagSerializer(tag_inst).data
            tag_term_data = tag_term_serializer.data
            del tag_term_data['tag']
            tag_data['term'] = tag_term_data['term']
        except Exception as e:
            print('create_tag failed: ', str(e))
            msg = '[portfolio_service][create_tag]' + str(e)
            self.logger_error.error(msg)
            raise BusinessLogicError(msg, None, None)
        else:
            self.result = tag_data

        return self.result

    def set_tag_term(self, tag_id, portfolio_term):
        pass

    def set_tags_with_portfolio_id(self, tag_list, portfolio_id):
        try:
            # tag_ids = [tag['id'] for tag in tag_list]
            if len(tag_list) > 0:
                tag_ids = tag_list
                print('tag_ids:', str(tag_ids))
                tag_qs = Tag.objects.filter(id__in=tag_ids)
                if tag_qs:
                    for tag in tag_qs:
                        portfolio_list = json.loads(tag.portfolios)
                        if portfolio_id not in portfolio_list:
                            portfolio_list.append(portfolio_id)
                        tag.portfolios = json.dumps(portfolio_list)
                        tag.save()
                tag_list_data = TagSerializer(tag_qs, many=True).data
            else:
                tag_list_data = []
        except Exception as e:
            msg = '[portfolio_service][set_tags_with_portfolio_id]' + str(e)
            print(msg)
            self.logger_error.error(msg)
            raise BusinessLogicError(msg, None, None)
        else:
            self.result = tag_list_data
        return self.result

    def set_tags_to_remove_portfolio_id(self, tag_list, portfolio_id):
        try:
            if len(tag_list) > 0:
                tag_ids = tag_list
                print('tag_ids:', str(tag_ids))
                tag_qs = Tag.objects.filter(id__in=tag_ids)
                if tag_qs:
                    for tag in tag_qs:
                        portfolio_list = json.loads(tag.portfolios)
                        if portfolio_id in portfolio_list:
                            portfolio_list.remove(portfolio_id)
                        tag.portfolios = json.dumps(portfolio_list)
                        tag.save()
                tag_list_data = TagSerializer(tag_qs, many=True).data
            else:
                tag_list_data = []
        except Exception as e:
            msg = '[portfolio_service][set_tags_to_remove_portfolio_id]' + str(e)
            print(msg)
            self.logger_error.error(msg)
            raise BusinessLogicError(msg, None, None)
        else:
            self.result = tag_list_data
        return self.result

    def get_tag_with_term(self, locale, term):
        try:
            tag_term_inst = TagTerm.objects.select_related('tag').get(term=term, locale=locale)
            print(str(tag_term_inst))
            tag_term_data = TagWithTermSerializer(tag_term_inst).data
        except Exception as e:
            msg = '[portfolio_service][get_tag_with_term]' + str(e)
            print(msg)
            self.logger_error.error(msg)
            raise BusinessLogicError(msg, None, None)
        else:
            self.result = tag_term_data
        return self.result

    def get_tag_list(self, locale, ids=None):
        try:
            tag_query = {'locale': locale, 'tag__is_activated': True}
            if ids is not None:
                tag_query['id__in'] = ids
            tag_qs = TagTerm.objects.filter(**tag_query).select_related('tag')
            # print('tag_qs:', str(tag_qs))
            tags_data = TagTermListSerializer(tag_qs, many=True).data
            print('tag_data: ', tags_data)
        except Exception as e:
            print('get_tag_list error:', str(e))
            self.result = None
        else:
            self.result = tags_data
        return self.result

    def validate_tag_ids(self, tag_ids):
        # check if the tag id exists
        count = Tag.objects.filter(id__in=tag_ids).count()

        if count == len(tag_ids):
            self.result = True
        else:
            self.result = False
        print('validate_tag_ids returns:', self.result)
        return self.result

    def get_all_tags_with_details(self, locale, tag_ids):
        # returns all tag-term even if it is not activated yet
        tag_query = {'locale': locale, 'tag__id__in': tag_ids}
        tag_qs = TagTerm.objects.filter(**tag_query).select_related('tag')
        tags_data = TagTermListSerializer(tag_qs, many=True).data
        print('tag_data: ', str(tags_data))
        self.result = tags_data

        return self.result






