from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [('employees', '0003_optional_contract_end_date')]

    operations = [
        migrations.AlterField(
            model_name='employee', name='gender',
            field=models.CharField(blank=True, null=True, max_length=1,
                                   choices=[('M', 'Male'), ('F', 'Female')]),
        ),
    ]
