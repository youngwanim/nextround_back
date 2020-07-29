from django.db import models


class User(models.Model):
    open_id = models.CharField(max_length=128)
    name = models.CharField(max_length=128)

    def __str__(self):
        return str(self.open_id)

    class Meta:
        ordering = ('-id', )


class UserLoginInfo(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    login_key = models.CharField(max_length=64)
    login_value = models.CharField(max_length=64)

    def __str__(self):
        return str(self.user.open_id) + ' : ' + str(self.login_key)

    class Meta:
        ordering = ('-id', )