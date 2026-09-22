from django.db import models

class Policy(models.Model):
    policy_name = models.CharField(max_length=100)
    min_service_years = models.IntegerField()
    max_service_years = models.IntegerField()
    days_per_year = models.IntegerField()
    effective_from = models.DateField()
    effective_to = models.DateField()
    allow_carry = models.BooleanField()
    max_allow_carry = models.IntegerField()
    accrual_method = models.CharField(max_length=100)
    notes = models.TextField()




