from .models import Portfolio, PortfolioContent
from rest_framework import serializers


class PortfolioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Portfolio
        fields = '__all__'


class PortfolioContentSerializer(serializers.ModelSerializer):
    class Meta:
        model = PortfolioContent
        fields = '__all__'

