from django.contrib import admin
#import hr.hr.employees.models

from employees.models import Department, Employee

admin.site.register(Employee)
admin.site.register(Department)
