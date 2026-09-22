from django.contrib import admin
#import hr.hr.employees.models

from employees.models import Employee

admin.site.register(Employee)