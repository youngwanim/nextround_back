from rana.users.service.user_service import UserService


class SignUpManager:

    def __init__(self, logger_info, logger_error):
        self.logger_info = logger_info
        self.logger_error = logger_error
        self.result = None
        self.user = None
        self.login_info = None
        self.user_service = UserService(self.logger_info, self.logger_error)

    def set_user_data(self, user_data, open_id=None):
        self.logger_info.info('[UserManager][set_user_data]set_user_data with : %s', str(user_data))
        try:
            if not open_id:
                # create new user instance
                new_user_data = self.user_service.create_new_user(user_data)
                print(str(new_user_data))
            else:
                pass
        except Exception as e:
            self.logger_info.info(str(e))
        else:
            self.result = new_user_data

        return self.result

    def check_user_exists(self, login_key):
        self.logger_info.info('[UserManager][check_user_exists]check user exists with : %s', str(login_key))
        try:
            is_exists = self.user_service.check_user_with_login_key(login_key)
        except Exception as e:
            print(e)
            self.logger_info.info(str(e))
            self.result = False
        else:
            self.result = is_exists

        return self.result

