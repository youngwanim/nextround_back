from django.urls import path
from rana.bplatform import views_token

urlpatterns = [
    path('token', views_token.Token.as_view(), name='token'),
]