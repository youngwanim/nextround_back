from django.db import models

# Create your models here.


class Portfolio(models.Model):
    open_id = models.CharField(max_length=128)
    corporation_name = models.CharField(max_length=64, default='', null=True, blank=True)
    brand_name = models.CharField(max_length=128, default='', null=True, blank=True)
    homepage_url = models.URLField(blank=True)
    created_date = models.DateTimeField(auto_now_add=True, blank=True)
    updated_date = models.DateTimeField(auto_now=True, blank=True)
    rank = models.IntegerField(default=0, blank=True)
    is_activated = models.BooleanField(default=False)  # admin modify this value after review
    ci_image = models.CharField(max_length=128, default='', null=True, blank=True)
    # JSON array containing tags <- need some validation for Tags model
    business_category = models.TextField(default='[]', null=True, blank=True)

    def __str__(self):
        return str(self.id) + ':' + str(self.open_id)

    class Meta:
        ordering = ('-id',)


class PortfolioContent(models.Model):
    portfolio = models.ForeignKey(Portfolio, related_name='content', on_delete=models.CASCADE)
    lang = models.SmallIntegerField(default=0)
    locale = models.CharField(default='ko', max_length=32, blank=True)
    auth_type = models.SmallIntegerField(default=3)
    title = models.CharField(max_length=128, default='', blank=True)
    sub_title = models.CharField(max_length=256, default='', blank=True)
    description = models.TextField(default='', blank=True)
    image_url = models.CharField(max_length=128, default='', blank=True) # thumbnail image on portfolio list page
    image_list = models.TextField(default='[]', null=True, blank=True)
    product_auth_type = models.SmallIntegerField(default=3)
    product_title = models.CharField(default='', max_length=128)
    product_sub_title = models.CharField(default='', max_length=128, blank=True)
    product_image_list = models.TextField(default='[]', null=True, blank=True)
    product_introduce = models.TextField(default='', null=True, blank=True)
    team_auth_type = models.SmallIntegerField(default=3)
    team_title = models.CharField(max_length=128, default='', blank=True)
    team_sub_title = models.CharField(max_length=128, default='', blank=True)
    team_image_list = models.TextField(default='[]', null=True, blank=True)
    team_introduce = models.TextField(default='', null=True, blank=True)
    ceo_auth_type = models.SmallIntegerField(default=3)
    ceo = models.CharField(max_length=64, default='', blank=True)
    ceo_sub_title = models.CharField(max_length=64, default='', blank=True)
    ceo_image_list = models.TextField(default='[]', null=True, blank=True)
    ceo_introduce = models.TextField(default='', null=True, blank=True)
    ir_auth_type = models.SmallIntegerField(default=3)
    ir_file = models.CharField(default='', max_length=128, null=True, blank=True)

    def __str__(self):
        return str(self.portfolio.id) + ':' + str(self.title)

    class Meta:
        ordering = ('-id',)


class Tag(models.Model):
    code = models.CharField(default='', max_length=32)
    portfolios = models.TextField(default='[]', null=True, blank=True)  # JSON array including portfolio ID
    is_activated = models.BooleanField(default=False, blank=True)

    def __str__(self):
        return str(self.code)

    class Meta:
        ordering = ('-id',)


class TagTerm(models.Model):
    tag = models.ForeignKey(Tag, related_name='term', on_delete=models.CASCADE)
    locale = models.CharField(default='ko', max_length=32, blank=True)
    term = models.CharField(default='', max_length=32)

    def __str__(self):
        return str(self.term)

    class Meta:
        ordering = ('-id',)
