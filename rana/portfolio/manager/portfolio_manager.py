import json

from rana.common.exceptions.exceptions import DataValidationError
from rana.portfolio.service.portfolio_service import PortfolioService


def check_dump(key, dict_data):
    return json.dumps(dict_data[key]) if key in dict_data else '[]'


def check_json(key, str_data):
    if key in str_data and type(str_data[key]) == str:
        return json.loads(str_data[key])
    else:
        return []


def text_to_json(portfolio):
    portfolio['business_category'] = check_json('business_category', portfolio)
    portfolio_content = portfolio.get('content', None)
    if portfolio_content is not None:
        portfolio_content['image_list'] = check_json('image_list', portfolio_content)
        portfolio_content['product_image_list'] = check_json('product_image_list', portfolio_content)
        portfolio_content['team_image_list'] = check_json('team_image_list', portfolio_content)
        portfolio_content['ceo_image_list'] = check_json('ceo_image_list', portfolio_content)
    # json_text['business_category'] = check_json('business_category', json_text)
    return portfolio


def json_to_text(portfolio, portfolio_content):
    portfolio['business_category'] = check_dump('business_category', portfolio)
    portfolio_content['image_list'] = check_dump('image_list', portfolio_content)
    portfolio_content['product_image_list'] = check_dump('product_image_list', portfolio_content)
    portfolio_content['team_image_list'] = check_dump('team_image_list', portfolio_content)
    portfolio_content['ceo_image_list'] = check_dump('ceo_image_list', portfolio_content)
    # portfolio_content['business_category'] = check_dump('business_category', portfolio_content)

    return portfolio_content


class PortfolioManager:
    def __init__(self, logger_info, logger_error):
        self.logger_info = logger_info
        self.logger_error = logger_error

        self.portfolio_service = PortfolioService(self.logger_info, self.logger_error)

    def create_my_portfolio(self, open_id, portfolio, portfolio_content):
        # check business category exists and it is valid
        tag_list = portfolio.get('business_category', [])
        print('tag_list:', str(tag_list))
        if len(tag_list) > 0 and not self.portfolio_service.validate_tag_ids(tag_list):
            msg = '[portfolio_manager][update_my_portfolio]Invalid business_category:{} by open id<{}>' \
                .format(str(tag_list), open_id)
            print(msg)
            raise DataValidationError(msg, None, None)

        content_data = json_to_text(portfolio, portfolio_content)
        result_portfolio = self.portfolio_service.create_my_portfolio_detail(open_id, portfolio, content_data)
        result_portfolio = text_to_json(result_portfolio)

        # Tag update should be followed
        tag_list_data = self.portfolio_service.set_tags_with_portfolio_id(tag_list, result_portfolio['id'])

        return result_portfolio, tag_list_data

    def get_my_portfolio_data_with_content(self, portfolio_data):
        portfolio_content_data = self.portfolio_service.get_my_portfolio_detail(portfolio_data['id'])
        portfolio_data['content'] = portfolio_content_data
        portfolio_data = text_to_json(portfolio_data)

        return portfolio_data

    def read_my_portfolios(self, open_id):
        portfolios_data = self.portfolio_service.get_my_portfolio_list(open_id)
        portfolios_res_data = [self.get_my_portfolio_data_with_content(portfolio_item)
                               for portfolio_item in portfolios_data]

        return portfolios_res_data

    def update_my_portfolio(self, open_id, portfolio_id, portfolio_data, portfolio_content_data):
        # check business category exists and it is valid
        tag_list = portfolio_data.get('business_category', [])
        if len(tag_list) > 0 and not self.portfolio_service.validate_tag_ids(tag_list):
            msg = '[portfolio_manager][update_my_portfolio]Invalid business_category:{} on portfolio id<{}>'\
                .format(str(tag_list), portfolio_id)
            raise DataValidationError(msg, None, None)
        portfolio_business_category_origin_list = self.portfolio_service.get_my_portfolio_business_category(portfolio_id)
        portfolio_content_data = json_to_text(portfolio_data, portfolio_content_data)
        portfolio_res_data = self.portfolio_service.set_my_portfolio_detail(open_id, portfolio_id,
                                                                            portfolio_data, portfolio_content_data)
        portfolio_res_data = text_to_json(portfolio_res_data)
        # Tag update should be followed
        tag_to_be_updated = list(set(portfolio_business_category_origin_list) - set(tag_list))
        self.portfolio_service.set_tags_to_remove_portfolio_id(tag_to_be_updated, portfolio_id)
        tag_list_data = self.portfolio_service.set_tags_with_portfolio_id(tag_list, portfolio_id)

        return portfolio_res_data, tag_list_data

    def read_portfolio(self, portfolio_id, user_type):
        portfolio_data = self.portfolio_service.get_portfolio_detail(portfolio_id, user_type)
        if portfolio_data is not None:
            portfolio_data = text_to_json(portfolio_data)

        return portfolio_data

    def read_portfolios_with_ids(self, page, limit, portfolio_ids=None):
        portfolio_list = self.portfolio_service.get_portfolio_list_by_ids(page, limit, portfolio_ids)
        return portfolio_list

    def read_portfolios_with_business_type(self, page, limit, business_types=None):
        portfolio_list = self.portfolio_service.get_portfolio_list(page, limit, business_types)
        return portfolio_list

    def read_tag_list(self, locale, ids=None):
        tag_list = self.portfolio_service.get_tag_list(locale, ids)
        return tag_list

    def get_or_create_tag(self, locale, term, portfolio_id=None):
        tag_exist = self.portfolio_service.check_tag_term_exist(term, locale)
        if tag_exist:
            print('input term already exists')
            tag_data = self.portfolio_service.get_tag_with_term(locale, term)
        else:
            print('create tag with input term')
            tag_term = {'term': term, 'locale': locale}
            tag_data = self.portfolio_service.create_tag(tag_term, portfolio_id)
        return tag_data

    def create_tag(self, tag_term, portfolio_id=None):
        # 0. consider user request the tag as list
        # 1. need to check tag_term.term already exists
        # 2. check portfolio in tag.portfolios exists. if not, just fail, not exception
        if not self.portfolio_service.check_tag_term_exist(tag_term['term'], tag_term['locale']):
            print('The tag term can be added')
            tag_data = self.portfolio_service.create_tag(tag_term, portfolio_id)
        else:
            msg = 'the term is already exists in DB'
            raise DataValidationError(msg, None)
        return tag_data

    def update_tag_with_portfolio(self, tag_list, portfolio_id):
        # returns selected tag list
        # tag_list is the objects list in which the object contains id of tag
        tag_data_list = self.portfolio_service.set_tags_with_portfolio_id(tag_list, portfolio_id)
        return tag_data_list






