from django.urls import re_path
from apps.dashboard import reports

urlpatterns = [
    re_path(r'^/general/?$', reports.get_general_report),
    re_path(r'^/sales/?$', reports.get_sales_report),
    re_path(r'^/warehouse/?$', reports.get_warehouse_report),
    re_path(r'^/production/?$', reports.get_production_report),
    re_path(r'^/finance/?$', reports.get_finance_report),
    re_path(r'^/services/?$', reports.get_services_report),
]
