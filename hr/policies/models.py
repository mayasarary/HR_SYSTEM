from django.db import models

class Policy(models.Model):
    policy_name = models.CharField(max_length=100)
    service_years = models.IntegerField()
    days_per_year = models.IntegerField()
    allow_carry = models.BooleanField()
    carry_forward_amount = models.IntegerField()
    notes = models.TextField()

    def __str__(self):
        pass


