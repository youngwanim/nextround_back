from django.db import models


# Auth platform domain
class AuthToken(models.Model):
    access_token = models.CharField(max_length=64, null=False, unique=True)
    access_token_state = models.IntegerField(null=False, default=0)
    user_open_id = models.CharField(max_length=64, null=False, unique=True)
    user_type = models.TextField(blank=False)
    is_active = models.BooleanField(default=False, blank=False)

    def __str__(self):
        return str(self.user_open_id)

    class Meta:
        ordering = ('id',)
