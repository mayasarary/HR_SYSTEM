from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [('employees', '0002_working_times')]

    operations = [
        migrations.AlterField(
            model_name='employee',
            name='contract_end_date',
            field=models.DateField(blank=True, null=True),
        ),
    ]
