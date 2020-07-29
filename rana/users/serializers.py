from rana.users.models import User, UserLoginInfo
from rest_framework import serializers


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = '__all__'


class UserLoginInfoSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = UserLoginInfo
        fields = ['user', 'login_key', 'login_value']
