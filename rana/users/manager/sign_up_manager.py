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
