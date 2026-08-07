from django.contrib import admin
from apps.warehouse.models import WarehouseStock, StockMovement
admin.site.register(WarehouseStock)
admin.site.register(StockMovement)
