from django.contrib import admin

# Register your models here.
from .models import User, UserLoginInfo

admin.site.register(User)
admin.site.register(UserLoginInfo)