from django.contrib import admin

# Register your models here.
from .models import Portfolio, PortfolioContent

admin.site.register(Portfolio)
admin.site.register(PortfolioContent)