from django.contrib.auth.models import User
from django.db import models


class User(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)
    last_loin_at = models.DateField(null=True, blank=True)

    def __str__(self):
        pass
