from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [('employees', '0006_employee_department_position')]

    operations = [
        migrations.AlterField(
            model_name='employee', name='position',
            field=models.CharField(blank=True, default='', max_length=20, choices=[
                ('ADMIN_MANAGER', 'المدير الاداري'),
                ('FINANCE_MANAGER', 'المدير المالي'),
                ('ENGINEER', 'مهندس اجهزة طبية'),
                ('SALES_REP', 'مندوب مبيعات'),
                ('SERVICES_WORKER', 'عامل خدمات'),
                ('ADMIN_STAFF', 'شؤون ادارية'),
                ('LAB_TECHNICIAN', 'فني مختبرات طبية'),
                ('INTERN', 'متدرب'),
            ]),
        ),
    ]
