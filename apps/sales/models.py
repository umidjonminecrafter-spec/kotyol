from django.db import models
from core.base_model import BaseModel

class Sale(BaseModel):
    invoice_number = models.CharField(max_length=50, unique=True)
    customer = models.ForeignKey('master_data.Customer', on_delete=models.CASCADE, db_column='customer_id', related_name='sales')
    boiler = models.ForeignKey('products.Boiler', on_delete=models.SET_NULL, null=True, blank=True, db_column='boiler_id', related_name='sales')
    product = models.ForeignKey('products.Product', on_delete=models.SET_NULL, null=True, blank=True, db_column='product_id', related_name='sales')
    quantity = models.DecimalField(max_digits=15, decimal_places=3)
    unit_price = models.DecimalField(max_digits=15, decimal_places=2)
    subtotal = models.DecimalField(max_digits=15, decimal_places=2)
    discount_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    tax_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    total_amount = models.DecimalField(max_digits=15, decimal_places=2)
    exchange_rate_at_creation = models.DecimalField(max_digits=10, decimal_places=4, default=1.0000)

    payment_status = models.CharField(max_length=20, default="UNPAID")
    delivery_status = models.CharField(max_length=20, default="PENDING")

    assigned_employee_id = models.CharField(max_length=36, null=True, blank=True)
    assigned_employee_name = models.CharField(max_length=255, null=True, blank=True)
    warranty_period = models.CharField(max_length=50, null=True, blank=True)
    warranty_start_date = models.DateField(null=True, blank=True)
    warranty_end_date = models.DateField(null=True, blank=True)
    delivery_location = models.CharField(max_length=255, null=True, blank=True)
    notes = models.TextField(null=True, blank=True)

    class Meta:
        db_table = 'sales'

class Order(BaseModel):
    order_number = models.CharField(max_length=50, unique=True, db_index=True)
    order_name = models.CharField(max_length=255, null=True, blank=True)
    customer = models.ForeignKey('master_data.Customer', on_delete=models.SET_NULL, null=True, blank=True, db_column='customer_id', related_name='orders')
    customer_name = models.CharField(max_length=255, null=True, blank=True)
    boiler = models.ForeignKey('products.Boiler', on_delete=models.SET_NULL, null=True, blank=True, db_column='boiler_id', related_name='orders')
    boiler_model_name = models.CharField(max_length=255, null=True, blank=True)
    quantity = models.DecimalField(max_digits=15, decimal_places=3, default=1.000)
    unit_price = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    total_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    priority = models.CharField(max_length=20, default="NORMAL")
    status = models.CharField(max_length=50, default="NEW")
    delivery_date = models.DateField(null=True, blank=True)
    deposit_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    auto_discount_on_late = models.BooleanField(default=True)
    late_discount_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0.50)
    assigned_employee_id = models.CharField(max_length=36, null=True, blank=True)
    assigned_employee_name = models.CharField(max_length=255, null=True, blank=True)
    notes = models.TextField(null=True, blank=True)

    class Meta:
        db_table = 'orders'

class Lead(BaseModel):
    full_name = models.CharField(max_length=255)
    phone = models.CharField(max_length=50)
    email = models.EmailField(max_length=255, null=True, blank=True)
    company_name = models.CharField(max_length=255, null=True, blank=True)
    status = models.CharField(max_length=50, default="NEW") # NEW, CONTACTED, OFFER, NEGOTIATION, WON, LOST
    source = models.CharField(max_length=100, null=True, blank=True)
    notes = models.TextField(null=True, blank=True)
    next_contact_date = models.DateField(null=True, blank=True)
    assigned_employee_id = models.CharField(max_length=36, null=True, blank=True)
    assigned_employee_name = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        db_table = 'leads'
