from django.db import models


class Event(models.Model):
    STATUS_CHOICES = [
        (0, 'Created'),
        (1, 'Waiting on D-day'),
        (2, 'Running'),
        (3, 'Terminated')
    ]
    event_number = models.IntegerField(unique=True)
    status = models.IntegerField(default=0, blank=True, choices=STATUS_CHOICES)
    start_datetime = models.DateTimeField()
    end_datetime = models.DateTimeField(null=True, blank=True)
    related_portfolios = models.TextField(default='[]', blank=True)
    country_code = models.CharField(default='82', blank=True)
    address_represent = models.CharField(default='', blank=True)
    address_lng = models.FloatField(default=0.0, blank=True)
    address_lat = models.FloatField(default=0.0, blank=True)

    def __str__(self):
        return str(self.id) + ':#' + str(self.event_number)

    class Meta:
        ordering = ('-id',)


class EventContent(models.Model):
    event = models.ForeignKey(Event, related_name='content', on_delete=models.CASCADE)
    event_name = models.CharField(default='', max_length=64, blank=True)
    lang = models.SmallIntegerField(default=0)
    locale = models.CharField(default='ko', max_length=32, blank=True)
    address = models.CharField(default='', max_length=256, blank=True)
    stream_url = models.CharField(default='', max_length=256, blank=True)
    message_created = models.TextField(default='', blank=True)
    message_waiting = models.TextField(default='', blank=True)
    message_running = models.TextField(default='', blank=True)
    message_terminated = models.TextField(default='', blank=True)

    def __str__(self):
        return str(self.event.id) + ':' + str(self.event.event_number)

    class Meta:
        ordering = ('-id',)







