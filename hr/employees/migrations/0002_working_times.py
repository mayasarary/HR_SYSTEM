from django.db import migrations, models
from django.utils import timezone


def copy_working_times(apps, schema_editor):
    Employee = apps.get_model('employees', 'Employee')
    employees = Employee.objects.using(schema_editor.connection.alias)
    for employee in employees.all().iterator():
        values = {}
        for name in ('working_start', 'working_end'):
            value = getattr(employee, name)
            if value is not None:
                if timezone.is_aware(value):
                    value = timezone.localtime(value)
                value = value.time()
            values[f'{name}_time'] = value
        employees.filter(pk=employee.pk).update(**values)


class Migration(migrations.Migration):
    dependencies = [('employees', '0001_initial')]

    operations = [
        migrations.AddField(
            model_name='employee', name='working_start_time',
            field=models.TimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='employee', name='working_end_time',
            field=models.TimeField(blank=True, null=True),
        ),
        migrations.RunPython(copy_working_times),
        migrations.RemoveField(model_name='employee', name='working_start'),
        migrations.RemoveField(model_name='employee', name='working_end'),
        migrations.RenameField(
            model_name='employee', old_name='working_start_time', new_name='working_start',
        ),
        migrations.RenameField(
            model_name='employee', old_name='working_end_time', new_name='working_end',
        ),
    ]
