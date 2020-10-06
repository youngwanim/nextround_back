from django.db import models


class User(models.Model):
    USER_TYPE = (
        (0, 'ADMIN'),
        (1, 'VC'),
        (2, 'STARTUP'),
        (3, 'ETC'),
        (4, 'RESERVED')
    )
    open_id = models.CharField(max_length=128)
    name = models.CharField(max_length=128)
    corporation_name = models.CharField(max_length=64, default='', blank=True)
    is_active = models.BooleanField(default=False, blank=True)  # mail certified
    qualified = models.BooleanField(default=False)  # Set by admin, if business card is certified
    access_token = models.CharField(max_length=64, blank=True)
    user_type = models.SmallIntegerField(default=3, choices=USER_TYPE)
    email = models.EmailField(max_length=254, null=True, blank=True)
    mdn = models.CharField(default='', max_length=32, blank=True)
    locale = models.CharField(max_length=5, default='ko', null=True)
    profile_image = models.CharField(max_length=256, blank=True, default='')
    created_date = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    last_visited_date = models.DateTimeField(auto_now=True, null=True, blank=True)
    address = models.CharField(default='', max_length=256, blank=True)
    business_card = models.CharField(default='', max_length=256, blank=True)  # url of the user's business card image

    def __str__(self):
        return str(self.name + ' : ' + self.email + ' : '+ self.open_id)

    class Meta:
        ordering = ('-id', )


class UserLoginInfo(models.Model):
    user = models.ForeignKey(User, related_name='userlogininfos', on_delete=models.CASCADE)
    login_key = models.CharField(max_length=64)   # id
    login_value = models.CharField(max_length=64)  # password

    def __str__(self):
        return str(self.user.open_id) + ' : ' + str(self.login_key)

    class Meta:
        ordering = ('-id', )

