from django.contrib import admin

# Register your models here.
from .models import Tag, TagTerm, Portfolio, PortfolioContent

admin.site.register(Tag)
admin.site.register(TagTerm)
admin.site.register(Portfolio)
admin.site.register(PortfolioContent)