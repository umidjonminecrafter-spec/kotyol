import core.base_model
import django.utils.timezone
from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('master_data', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='SalaryType',
            fields=[
                ('id', models.CharField(default=core.base_model.generate_uuid, editable=False, max_length=36, primary_key=True, serialize=False)),
                ('status', models.CharField(default='ACTIVE', max_length=20)),
                ('is_active', models.BooleanField(default=True)),
                ('organization_id', models.CharField(blank=True, max_length=36, null=True)),
                ('branch_id', models.CharField(blank=True, max_length=36, null=True)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('updated_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('created_by_id', models.CharField(blank=True, max_length=36, null=True)),
                ('updated_by_id', models.CharField(blank=True, max_length=36, null=True)),
                ('code', models.CharField(max_length=50, unique=True)),
                ('name', models.CharField(max_length=255)),
                ('description', models.TextField(blank=True, null=True)),
            ],
            options={
                'db_table': 'salary_types',
            },
        ),
    ]
