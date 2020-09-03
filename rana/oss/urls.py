from django.urls import path
from rana.oss import views

urlpatterns = [
    path('upload', views.OssFile.as_view(), name='upload'),
]
