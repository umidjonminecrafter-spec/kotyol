from django.db import models
from core.base_model import BaseModel

class ProductCategory(BaseModel):
    code = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)

    class Meta:
        db_table = 'product_categories'

class SupplierCategory(BaseModel):
    code = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)

    class Meta:
        db_table = 'supplier_categories'

class MaterialType(BaseModel):
    code = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)

    class Meta:
        db_table = 'material_types'

class Unit(BaseModel):
    code = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=255)
    symbol = models.CharField(max_length=20, null=True, blank=True)

    class Meta:
        db_table = 'units'

class Supplier(BaseModel):
    code = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=255)
    contact_name = models.CharField(max_length=255, null=True, blank=True)
    phone = models.CharField(max_length=50, null=True, blank=True)
    email = models.CharField(max_length=255, null=True, blank=True)
    address = models.TextField(null=True, blank=True)

    class Meta:
        db_table = 'suppliers'

class Customer(BaseModel):
    code = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=255)
    contact_name = models.CharField(max_length=255, null=True, blank=True)
    phone = models.CharField(max_length=50, null=True, blank=True)
    email = models.CharField(max_length=255, null=True, blank=True)
    address = models.TextField(null=True, blank=True)

    class Meta:
        db_table = 'customers'

class Warehouse(BaseModel):
    code = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=255)
    location = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        db_table = 'warehouses'

class WarrantyType(BaseModel):
    code = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=255)
    months = models.DecimalField(max_digits=5, decimal_places=0, default=12)

    class Meta:
        db_table = 'warranty_types'

class CustomerType(BaseModel):
    code = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=255)

    class Meta:
        db_table = 'customer_types'

class ServiceType(BaseModel):
    code = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=255)

    class Meta:
        db_table = 'service_types'

class Priority(BaseModel):
    code = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=255)

    class Meta:
        db_table = 'priorities'

class OrderStatus(BaseModel):
    code = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=255)

    class Meta:
        db_table = 'order_statuses'

class ExpenseType(BaseModel):
    code = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=255)

    class Meta:
        db_table = 'expense_types'

class SalaryType(BaseModel):
    code = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    description = models.TextField(null=True, blank=True)

    class Meta:
        db_table = 'salary_types'

class ProductionStage(BaseModel):
    code = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=255)
    sequence = models.IntegerField(default=0)
    description = models.TextField(null=True, blank=True)

    class Meta:
        db_table = 'production_stages'

class InsuranceType(BaseModel):
    code = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)

    class Meta:
        db_table = 'insurance_types'

class Currency(BaseModel):
    code = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=255)
    symbol = models.CharField(max_length=20, default="$")
    exchange_rate = models.DecimalField(max_digits=12, decimal_places=4, default=1.0000)

    class Meta:
        db_table = 'currencies'

class DefectReason(BaseModel):
    code = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)

    class Meta:
        db_table = 'defect_reasons'

class Role(BaseModel):
    code = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)

    class Meta:
        db_table = 'roles'

class PermissionsMatrix(BaseModel):
    code = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=255)
    module = models.CharField(max_length=100, default="GENERAL")
    description = models.TextField(null=True, blank=True)

    class Meta:
        db_table = 'permissions_matrix'


class Company(BaseModel):
    name = models.CharField(max_length=255)
    phone = models.CharField(max_length=50, null=True, blank=True)
    website = models.CharField(max_length=255, null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    currency = models.CharField(max_length=20, default="USD")
    timezone = models.CharField(max_length=100, default="Asia/Tashkent (UTC+5)")
    date_format = models.CharField(max_length=50, default="YYYY-MM-DD")

    class Meta:
        db_table = 'company_profile'


class ServiceTicket(BaseModel):
    service_number = models.CharField(max_length=50, null=True, blank=True)
    customer_id = models.CharField(max_length=100, null=True, blank=True)
    customer_name = models.CharField(max_length=255, null=True, blank=True)
    boiler_id = models.CharField(max_length=100, null=True, blank=True)
    boiler_model_name = models.CharField(max_length=255, null=True, blank=True)
    service_type_id = models.CharField(max_length=100, null=True, blank=True)
    service_type_name = models.CharField(max_length=255, null=True, blank=True)
    assigned_employee_id = models.CharField(max_length=100, null=True, blank=True)
    assigned_employee_name = models.CharField(max_length=255, null=True, blank=True)
    service_date = models.CharField(max_length=50, null=True, blank=True)
    priority = models.CharField(max_length=50, default="NORMAL")
    status = models.CharField(max_length=50, default="NEW")
    is_under_warranty = models.BooleanField(default=True)
    warranty_period = models.CharField(max_length=100, null=True, blank=True)
    sale_date = models.CharField(max_length=50, null=True, blank=True)
    order_number = models.CharField(max_length=100, null=True, blank=True)
    production_number = models.CharField(max_length=100, null=True, blank=True)
    notes = models.TextField(null=True, blank=True)
    sale_id = models.CharField(max_length=100, null=True, blank=True)
    sale_invoice_number = models.CharField(max_length=100, null=True, blank=True)
    service_cost = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    employee_cost = models.DecimalField(max_digits=15, decimal_places=2, default=0.00, null=True, blank=True)

    class Meta:
        db_table = 'service_tickets'

