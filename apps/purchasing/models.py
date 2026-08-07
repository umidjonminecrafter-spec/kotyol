from django.db import models
from core.base_model import BaseModel

class Purchase(BaseModel):
    purchase_number = models.CharField(max_length=50, unique=True)
    supplier = models.ForeignKey('master_data.Supplier', on_delete=models.CASCADE, db_column='supplier_id', related_name='purchases')
    warehouse = models.ForeignKey('master_data.Warehouse', on_delete=models.CASCADE, db_column='warehouse_id', related_name='purchases')
    invoice_number = models.CharField(max_length=100, null=True, blank=True)
    order_date = models.DateField()
    subtotal = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    tax_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    total_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    exchange_rate_at_creation = models.DecimalField(max_digits=10, decimal_places=4, default=1.0000)
    status = models.CharField(max_length=20, default="DRAFT")

    class Meta:
        db_table = 'purchases'

class PurchaseItem(BaseModel):
    purchase = models.ForeignKey('Purchase', on_delete=models.CASCADE, db_column='purchase_id', related_name='items')
    product = models.ForeignKey('products.Product', on_delete=models.CASCADE, db_column='product_id', related_name='purchase_items')
    quantity = models.DecimalField(max_digits=15, decimal_places=3)
    unit_price = models.DecimalField(max_digits=15, decimal_places=2)
    total_price = models.DecimalField(max_digits=15, decimal_places=2)

    class Meta:
        db_table = 'purchase_items'
