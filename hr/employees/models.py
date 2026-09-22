from django.conf import settings
from django.contrib.auth.models import User
from django.db import models

class Employee(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='employee')
    full_name = models.CharField(max_length=100)
    gender = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=30)
    email = models.EmailField()
    address = models.TextField()
    date_of_birth = models.DateField()
    hire_date = models.DateField()
    employment_status = models.BooleanField(default=False)
    contract_type = models.CharField(max_length=100)
    contract_start_date = models.DateField()
    contract_end_date = models.DateField()
    basic_salary = models.IntegerField()
    currency_code = models.CharField(max_length=3)


    def __str__(self):
        pass

class AttendanceRecords(models.Model):
    employee = models.ForeignKey('Employee', on_delete=models.CASCADE, null=True, blank=True)
    attendance_date = models.DateField()
    schedule_start_date = models.DateField()
    schedule_end_date = models.DateField()
    check_in_date = models.DateField()
    check_out_date = models.DateField()
    status = models.CharField(max_length=100)
    late_minutes = models.IntegerField()
    early_departure = models.IntegerField()
    overtime_minutes = models.IntegerField()
    notes = models.TextField()



