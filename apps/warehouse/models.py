from django.db import models
from core.base_model import BaseModel

class WarehouseStock(BaseModel):
    warehouse = models.ForeignKey('master_data.Warehouse', on_delete=models.CASCADE, db_column='warehouse_id', related_name='stocks')
    product = models.ForeignKey('products.Product', on_delete=models.CASCADE, db_column='product_id', related_name='warehouse_stocks')
    quantity = models.DecimalField(max_digits=15, decimal_places=3, default=0.000)
    reserved_quantity = models.DecimalField(max_digits=15, decimal_places=3, default=0.000)
    avg_unit_cost = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)

    class Meta:
        db_table = 'warehouse_stock'
        unique_together = ('warehouse', 'product')

class StockMovement(BaseModel):
    movement_type = models.CharField(max_length=50)
    product = models.ForeignKey('products.Product', on_delete=models.CASCADE, db_column='product_id', related_name='stock_movements')
    warehouse = models.ForeignKey('master_data.Warehouse', on_delete=models.CASCADE, db_column='warehouse_id', related_name='stock_movements')
    quantity = models.DecimalField(max_digits=15, decimal_places=3)
    reference_id = models.CharField(max_length=100, null=True, blank=True)
    notes = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        db_table = 'stock_movements'
