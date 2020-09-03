from rana.users.service.user_service import UserService


class SignInManager:

    def __init__(self, logger_info, logger_error):
        self.logger_info = logger_info
        self.logger_error = logger_error
        self.result = None
        self.user = None
        self.login_info = None
        self.user_service = UserService(self.logger_info, self.logger_error)

    def set_login_data(self, login_key, login_value):
        self.logger_info.info('[UserManager][[set_login_data]%s : %s', str(login_key), str(login_value))
        try:
            user_login_instance = self.user_service.get_login_info_with_key_value(
                login_key, login_value
            )
            user_data = self.user_service.get_user_data_with_ins(user_login_instance.user)
        except Exception as e:
            self.logger_info.info(str(e))
        else:
            self.result = user_data

        return self.result


