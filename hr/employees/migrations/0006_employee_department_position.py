from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [('employees', '0005_alter_attendancerecords_late_minutes_and_more')]

    operations = [
        migrations.AddField(
            model_name='employee', name='department',
            field=models.CharField(blank=True, default='', max_length=20, choices=[
                ('ADMIN', 'الشؤون الادارية'), ('FINANCE', 'الشؤون المالية'),
                ('ENGINEERING', 'الهندسة والصيانة'), ('SALES', 'المبيعات'),
                ('SERVICES', 'الخدمات'), ('WAREHOUSES', 'المستودعات'),
                ('BIOLINE', 'مختبر بيولاين'),
            ]),
        ),
        migrations.AddField(
            model_name='employee', name='position',
            field=models.CharField(blank=True, default='', max_length=20, choices=[
                ('MANAGER', 'Manager'), ('SUPERVISOR', 'Supervisor'),
                ('ACCOUNTANT', 'Accountant'), ('ENGINEER', 'Engineer'),
                ('TECHNICIAN', 'Technician'), ('SALES_REP', 'Sales Representative'),
                ('WAREHOUSE_KEEPER', 'Warehouse Keeper'),
                ('LAB_TECHNICIAN', 'Laboratory Technician'), ('EMPLOYEE', 'Employee'),
            ]),
        ),
    ]
