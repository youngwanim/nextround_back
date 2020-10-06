import json
from rana.portfolio.models import Portfolio, PortfolioContent, Tag, TagTerm
from rest_framework import serializers


class PortfolioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Portfolio
        fields = '__all__'


class PortfolioContentSerializer(serializers.ModelSerializer):
    class Meta:
        model = PortfolioContent
        exclude = ('id',)
        # fields = '__all__'


class PortfolioContentListSerializer(serializers.ModelSerializer):
    portfolio = PortfolioSerializer()

    class Meta:
        model = PortfolioContent
        fields = ('portfolio', 'auth_type', 'title', 'sub_title', 'image_url',)

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        # ret['id'] = ret.pop('portfolio')
        ret['id'] = ret['portfolio']['id']
        ret['business_category'] = json.loads(ret['portfolio']['business_category'])
        del ret['portfolio']
        return ret


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret['portfolios'] = json.loads(ret['portfolios'])
        del ret['code']
        return ret


class TagTermSerializer(serializers.ModelSerializer):
    class Meta:
        model = TagTerm
        exclude = ('id',)


class TagWithTermSerializer(serializers.ModelSerializer):
    tag = TagSerializer()

    class Meta:
        model = TagTerm
        fields = ('tag', 'locale', 'term',)

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret['id'] = ret['tag']['id']
        ret['portfolios'] = ret['tag']['portfolios']
        del ret['locale']
        del ret['tag']
        return ret


class TagTermListSerializer(serializers.ModelSerializer):
    tag = TagSerializer()

    class Meta:
        model = TagTerm
        fields = ('tag', 'term',)

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret['id'] = ret['tag']['id']
        ret['portfolios'] = ret['tag']['portfolios']
        del ret['tag']
        return ret

