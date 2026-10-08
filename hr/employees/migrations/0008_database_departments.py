import django.db.models.deletion
import employees.models
from django.db import migrations, models


def create_departments(apps, schema_editor):
    Department = apps.get_model('employees', 'Department')
    Employee = apps.get_model('employees', 'Employee')
    alias = schema_editor.connection.alias
    departments = Department.objects.using(alias)
    employees = Employee.objects.using(alias)
    initial = [
        ('ADMIN', 'الشؤون الادارية'), ('FINANCE', 'الشؤون المالية'),
        ('ENGINEERING', 'الهندسة والصيانة'), ('SALES', 'المبيعات'),
        ('SERVICES', 'الخدمات'), ('WAREHOUSES', 'المستودعات'),
        ('BIOLINE', 'مختبر بيولاين'),
    ]
    for code, name in initial:
        departments.get_or_create(code=code, defaults={'name': name})
    for code in employees.exclude(department='').values_list('department', flat=True).distinct():
        departments.get_or_create(code=code, defaults={'name': code})
        employees.filter(department=code).update(department_record_id=code)


def restore_department_codes(apps, schema_editor):
    Employee = apps.get_model('employees', 'Employee')
    employees = Employee.objects.using(schema_editor.connection.alias)
    for employee in employees.all().iterator():
        employees.filter(pk=employee.pk).update(department=employee.department_record_id or '')


class Migration(migrations.Migration):
    dependencies = [('employees', '0007_company_position_choices')]

    operations = [
        migrations.CreateModel(
            name='Department',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(default=employees.models.department_code, editable=False, max_length=20, unique=True)),
                ('name', models.CharField(max_length=100, unique=True)),
            ],
            options={'ordering': ['pk']},
        ),
        migrations.AddField(
            model_name='employee', name='department_record',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT,
                                    related_name='employees', to='employees.department', to_field='code'),
        ),
        migrations.RunPython(create_departments, restore_department_codes),
        migrations.RemoveField(model_name='employee', name='department'),
        migrations.RenameField(model_name='employee', old_name='department_record', new_name='department'),
    ]
