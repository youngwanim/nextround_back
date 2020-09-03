from django.urls import path
from rana.users import views_user

urlpatterns = [
    path('signin', views_user.UserSignIn.as_view(), name='signin'),
    path('signup', views_user.UserSignUp.as_view(), name='signup'),
    path('<open_id>', views_user.User.as_view(), name='user'),
    path('validation', views_user.UserValidation.as_view(), name='validation')
]