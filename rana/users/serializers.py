from rana.users.models import User, UserLoginInfo
from rest_framework import serializers


#class UserSerializer(serializers.HyperlinkedModelSerializer):
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        exclude = ('open_id', 'access_token', 'created_date', 'last_visited_date')


class UserAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'


class UserLoginInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserLoginInfo
        fields = ('user', 'login_key', 'login_value',)


class UserLoginInfoKeySerializer(serializers.ModelSerializer):
    class Meta:
        model = UserLoginInfo
        fields = ('login_key',)


class UserSigninSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('open_id', 'name', 'corporation_name',
                  'is_active', 'qualified', 'access_token', 'user_type', 'email',
                  'mdn', 'profile_image', 'address', 'business_card',)
