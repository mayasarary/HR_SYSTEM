
#class User(models.Model):
#    employee = models.ForeignKey('Employee', on_delete=models.CASCADE, null=True, blank=True)
  #  user_name = models.CharField(max_length=100)
   # email = models.EmailField()
    #password_hash = models.CharField(max_length=100)
  #  is_active = models.BooleanField(default=True)
  #  last_login_at = models.DateTimeField()

from django.contrib.auth.models import User
from django.db import models


class User(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)
    last_loin_at = models.DateField(null=True, blank=True)



    def __str__(self):
        pass
