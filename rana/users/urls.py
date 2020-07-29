from django.urls import path
from rana.users import views

urlpatterns = [
    path('', views.UserList.as_view()),
]