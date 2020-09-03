from django.db import models

# Create your models here.


class Portfolio(models.Model):
    INVEST_ROUND = (
        (0, 'SEED'),
        (1, 'Series A'),
        (2, 'Series B'),
        (3, 'Series C'),
    )

    open_id = models.CharField(max_length=128)
    portfolio_id = models.CharField(default='', max_length=128 )
    corporation_name = models.CharField(max_length=64, default='', null=True, blank=True)
    brand_name = models.CharField(max_length=128, default='', null=True, blank=True)
    homepage_url = models.URLField(blank=True)
    ceo = models.CharField(max_length=64, default='', blank=True)
    nr_participated = models.BooleanField(default=False)
    nr_participate_number = models.TextField(default='[]', blank=True)  # JSON array containing # of nr participation
    created_date = models.DateTimeField(auto_now_add=True, blank=True)
    updated_date = models.DateTimeField(auto_now=True, blank=True)
    rank = models.IntegerField(default=0, blank=True)
    is_activated = models.BooleanField(default=False)  # admin modify this value after review
    requested_hidden = models.BooleanField(default=False)
    ci_image = models.URLField(blank=True)
    funding_round = models.SmallIntegerField(default=0, choices=INVEST_ROUND)

    def __str__(self):
        return str(self.brand_name)

    class Meta:
        ordering = ('-id',)


class PortfolioContent(models.Model):
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE)
    lang = models.SmallIntegerField(default=0)
    title_image_url = models.URLField(null=False, blank=False)
    media_url = models.TextField(default='', blank=True)  # JSON array including image or video URL
    thumbnail = models.CharField(max_length=128, blank=True)  # thumbnail image on portfolio list page
    title = models.CharField(max_length=128, default='', blank=True)
    subtitle = models.CharField(max_length=256, default='', blank=True)
    description = models.TextField(default='', blank=True)
    industry = models.CharField(max_length=128, default='', blank=True)
    tags = models.TextField(default='')  # JSON array containing tags <- need some validation for Tags model
    partner = models.CharField(default='', max_length=128, blank=True)
    tech = models.CharField(default='', max_length=256,  blank=True)  # tech the service is based on
    ir_clip_url = models.CharField(default='', max_length=128, blank=True)  # url of IR video clip on our media server
    ir_clip_access = models.SmallIntegerField(default=0, )
    ir_doc_url = models.CharField(default='', blank=True)
    ir_doc_access = models.SmallIntegerField(default=0)

    def __str__(self):
        return str(self.portfolio.brand_name)

    class Meta:
        ordering = ('-id',)


class Tags(models.Model):
    term = models.CharField(default='', max_length=32)
    portfolios = models.TextField(default='')  # JSON array including portfolio ID

    def __str__(self):
        return str(self.term)


