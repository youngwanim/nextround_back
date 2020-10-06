from django.urls import path
from rana.users import views_user

urlpatterns = [
    path('', views_user.UserInfo.as_view(), name='user'),
    path('signin', views_user.UserSignIn.as_view(), name='signin'),
    path('signup', views_user.UserSignUp.as_view(), name='signup'),
    path('validation', views_user.UserValidation.as_view(), name='validation'),
    path('businesscard', views_user.UserHandleBCFile.as_view(), name='uploadImage'),
    #path('profile', views_user.UserHandlePFFile.as_view(), name='uploadImage'),
    path('info', views_user.UserInfo.as_view(), name='userinfo'),
    path('id/<login_key>', views_user.UserExists.as_view(), name='checkDuplicate'),
]