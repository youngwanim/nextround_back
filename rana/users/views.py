from rana.users.models import User, UserLoginInfo
from rana.users.serializers import UserSerializer, UserLoginInfoSerializer
from django.http import Http404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status


class UserList(APIView):

    def get(self, request, format=None):
        users = User.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)

    def post(self, request, ):
        request_data = request.data
        serializer = UserSerializer(data=request_data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserLoginInfoDetail(APIView):

    def get(self, request, open_id):
        try:
            user_obj = User.objects.get(open_id=open_id)
        except User.DoesNotExist:
            raise Http404
        try:
            user_login_info_obj = UserLoginInfo.objects.get(user=user_obj)
            user_login_info_serializer = UserLoginInfoSerializer(user_login_info_obj)
        except UserLoginInfo.DoesNotExist:
            raise Http404

        return Response(user_login_info_serializer.data)


