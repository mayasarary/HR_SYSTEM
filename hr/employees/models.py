from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
import uuid


def department_code():
    return uuid.uuid4().hex[:20]


class Department(models.Model):
    code = models.CharField(max_length=20, unique=True, default=department_code, editable=False)
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        ordering = ['pk']

    def __str__(self):
        return self.name


class Employee(models.Model):
    class DepartmentChoices(models.TextChoices):
        ADMINISTRATION = 'ADMIN', 'الشؤون الادارية'
        FINANCE = 'FINANCE', 'الشؤون المالية'
        ENGINEERING = 'ENGINEERING', 'الهندسة والصيانة'
        SALES = 'SALES', 'المبيعات'
        SERVICES = 'SERVICES', 'الخدمات'
        WAREHOUSES = 'WAREHOUSES', 'المستودعات'
        BIOLINE = 'BIOLINE', 'مختبر بيولاين'

    class PositionChoices(models.TextChoices):
        ADMIN_MANAGER = 'ADMIN_MANAGER', 'المدير الاداري'
        FINANCE_MANAGER = 'FINANCE_MANAGER', 'المدير المالي'
        ENGINEER = 'ENGINEER', 'مهندس اجهزة طبية'
        SALES_REP = 'SALES_REP', 'مندوب مبيعات'
        SERVICES_WORKER = 'SERVICES_WORKER', 'عامل خدمات'
        ADMIN_STAFF = 'ADMIN_STAFF', 'شؤون ادارية'
        LAB_TECHNICIAN = 'LAB_TECHNICIAN', 'فني مختبرات طبية'
        INTERN = 'INTERN', 'متدرب'

    class GenderChoices(models.TextChoices):
        MALE = 'M', 'Male'
        FEMALE = 'F', 'Female'

    class ContractTypeChoices(models.TextChoices):
        FULL_TIME = 'FT', 'Full-Time'
        PART_TIME = 'PT', 'Part-Time'
        CONTRACTOR = 'CON', 'Contractor'
        INTERN = 'INT', 'Intern'

    class CurrencyChoices(models.TextChoices):
        USD = 'USD', 'USD ($)'
        ILS = 'ILS', 'ILS (₪)'
        JOD = 'JOD', 'JOD (JD)'

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='employees'
    )
    full_name = models.CharField(max_length=100)
    department = models.ForeignKey(Department, to_field='code', on_delete=models.PROTECT,
                                   related_name='employees', blank=True, null=True)
    position = models.CharField(max_length=20, choices=PositionChoices.choices, blank=True, default='')

    gender = models.CharField(
        max_length=1,
        choices=GenderChoices.choices,
        blank=True,
        null=True
    )

    phone_number = models.CharField(max_length=30)
    email = models.EmailField()
    address = models.TextField()
    date_of_birth = models.DateField()
    hire_date = models.DateField()
    employment_status = models.BooleanField(default=False)

    contract_type = models.CharField(
        max_length=3,
        choices=ContractTypeChoices.choices,
        default=ContractTypeChoices.FULL_TIME
    )

    contract_start_date = models.DateField()
    contract_end_date = models.DateField(null=True, blank=True)
    basic_salary = models.IntegerField()

    currency_code = models.CharField(
        max_length=3,
        choices=CurrencyChoices.choices,
        default=CurrencyChoices.USD
    )

    working_start = models.TimeField(null=True, blank=True)
    working_end = models.TimeField(null=True, blank=True)

    def clean(self):
        super().clean()
        if self.contract_type == self.ContractTypeChoices.FULL_TIME:
            self.contract_end_date = None
        elif self.contract_type in self.ContractTypeChoices.values and not self.contract_end_date:
            raise ValidationError({
                'contract_end_date': _('Contract end date is required for this contract type.')
            })

    def __str__(self):
        return self.full_name

    def get_department_display(self):
        return self.department.name if self.department_id else ''


class AttendanceRecords(models.Model):
    class AttendanceStatus(models.TextChoices):
        PRESENT = 'PRESENT', 'Present'
        ABSENT = 'ABSENT', 'Absent'
        LATE = 'LATE', 'Late'
        LEAVE = 'LEAVE', 'On Leave'

    employee = models.ForeignKey('Employee', on_delete=models.CASCADE, null=False, blank=False)
    attendance_date = models.DateTimeField()
    check_in_date = models.DateTimeField()
    check_out_date = models.DateTimeField()

    status = models.CharField(
        max_length=15,
        choices=AttendanceStatus.choices,
        default=AttendanceStatus.PRESENT
    )

    late_minutes = models.IntegerField(default=0)
    overtime_minutes = models.IntegerField(default=0)
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.employee.full_name} - {self.attendance_date.strftime('%Y-%m-%d')}"
