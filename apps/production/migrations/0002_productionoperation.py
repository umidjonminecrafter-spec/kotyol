import core.base_model
import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('production', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProductionOperation',
            fields=[
                ('id', models.CharField(default=core.base_model.generate_uuid, editable=False, max_length=36, primary_key=True, serialize=False)),
                ('status', models.CharField(default='PENDING', max_length=30)),
                ('is_active', models.BooleanField(default=True)),
                ('organization_id', models.CharField(blank=True, max_length=36, null=True)),
                ('branch_id', models.CharField(blank=True, max_length=36, null=True)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('updated_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('created_by_id', models.CharField(blank=True, max_length=36, null=True)),
                ('updated_by_id', models.CharField(blank=True, max_length=36, null=True)),
                ('operation_name', models.CharField(max_length=255)),
                ('worker_id', models.CharField(blank=True, max_length=36, null=True)),
                ('worker_name', models.CharField(blank=True, max_length=255, null=True)),
                ('rate', models.DecimalField(decimal_places=2, default=0.0, max_digits=12)),
                ('batch', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='operations', to='production.productionbatch')),
            ],
            options={
                'db_table': 'production_operations',
            },
        ),
    ]
