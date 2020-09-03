import datetime
import json
import uuid

import requests
from django.db import transaction

from rana.common import urlmapper, code
from rana.common.models import ResultResponse
from rana.users.models import User, UserLoginInfo
from rana.users.serializers import UserSerializer


class UserService:

    def __init__(self, logger_info, logger_error):
        self.result = None
        self.logger_info = logger_info
        self.logger_error = logger_error

    def get_login_info_with_key_value(self, login_key, login_value):
        try:
            login_info = UserLoginInfo.objects.get(login_key=login_key, login_value=login_value)
        except Exception as e:
            print(e)
            self.result = None
        else:
            self.result = login_info

        return self.result

    def get_user_instance(self, open_id):
        try:
            user_qs = User.objects.filter(open_id=open_id)
            if user_qs.count() == 1:
                user_instance = User.objects.get(open_id=open_id)
            else:
                user_instance = None
        except Exception as e:
            self.logger_info.info(str(e))
        else:
            self.result = user_instance
        return self.result

    def get_user_data_with_ins(self, user_instance):
        try:
            user_data = UserSerializer(user_instance).data
        except Exception as e:
            self.logger_info.info(str(e))
        else:
            self.result = user_data

        return self.result

    def get_user_data_with_openid(self, open_id):
        try:
            user_instance = self.get_user_instance(open_id)
            user_data = self.get_user_data_with_ins(user_instance)
        except Exception as e:
            self.logger_info.info(str(e))
        else:
            self.result = user_data
        return self.result

    def set_user_active(self, user_instance, is_active):
        pass

    def set_user_qualified(self, user_instance, qualified):
        pass

    def create_new_user(self, user_data):
        try:
            user_instance = User.objects.create(
                open_id=user_data['open_id'],
                name=user_data['name'],
                corporation_name=user_data['corporation_name'],
                access_token=user_data['token'],
                user_type=user_data['user_type'],
                email=user_data['email'],
                mdn=user_data['mdn'],
                # profile_image=user_data['profile_image'],
                address=user_data['address'],
            )
            UserLoginInfo.objects.create(
                user=user_instance,
                login_key=user_data['login_key'],
                login_value=user_data['login_value']
            )

        except Exception as e:
            print('[user_service][create_new_user]Exception happens while creating user instance')
            self.logger_info.info(str(e))
        else:
            self.result = UserSerializer(user_instance).data
        return self.result

    def set_user_business_card(self, business_card_url):
        pass

