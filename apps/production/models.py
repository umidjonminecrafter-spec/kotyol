from django.db import models
from core.base_model import BaseModel

class ProductionBatch(BaseModel):
    batch_number = models.CharField(max_length=50, unique=True)
    boiler = models.ForeignKey('products.Boiler', on_delete=models.CASCADE, db_column='boiler_id', related_name='production_batches')
    target_quantity = models.IntegerField()
    completed_quantity = models.IntegerField(default=0)
    defect_quantity = models.IntegerField(default=0)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=30, default="PLANNED")
    assigned_employee = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        db_table = 'production_batches'

class ProductionOperation(BaseModel):
    batch = models.ForeignKey(ProductionBatch, on_delete=models.CASCADE, related_name='operations')
    operation_name = models.CharField(max_length=255)
    worker_id = models.CharField(max_length=36, null=True, blank=True)
    worker_name = models.CharField(max_length=255, null=True, blank=True)
    rate = models.DecimalField(max_digits=12, decimal_places=2, default=0.0)
    status = models.CharField(max_length=30, default="PENDING")

    class Meta:
        db_table = 'production_operations'
