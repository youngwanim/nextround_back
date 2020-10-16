import json
from rana.event.models import Event, EventContent
from rest_framework import serializers


class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        field = '__all__'


class EventContentSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventContent
        fields = '__all__'


class EventFullSerializer(serializers.ModelSerializer):
    contents = EventContentSerializer(many=True)

    class Meta:
        model = Event
        fields = ('event_number', 'status', 'start_datetime', 'end_datetime',
                  'related_portfolios', 'address_represent', 'contents',)
        # fields = ('event', 'event_name', 'address', 'stream_url',
        #           'message_created', 'message_waiting', 'message_running',
        #           'message_terminated',)

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret['related_portfolios'] = json.loads(ret['related_portfolios'])
        return ret
        # ret['id'] = ret['event']['id']
        # ret['related_portfolios'] = json.loads(ret['event']['related_portfolios'])
        # ret['start_datetime'] = ret['event']['start_datetime']
        # ret['end_datetime'] = ret['event']['end_datetime']
        # ret['event_number'] = ret['event']['event_number']
        # ret['address_represent']
        # ret['']

