from django.contrib import admin
from apps.purchasing.models import Purchase, PurchaseItem
admin.site.register(Purchase)
admin.site.register(PurchaseItem)
