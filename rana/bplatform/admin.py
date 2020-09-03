from django.contrib import admin

# Register your models here.
from .models import AuthToken

admin.site.register(AuthToken)