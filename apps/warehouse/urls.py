from django.urls import re_path
from apps.warehouse import views

urlpatterns = [
    re_path(r'^/stocks/(?P<id>[^/]+)/update/?$', views.warehouse_stock_detail_view),
    re_path(r'^/stocks/(?P<id>[^/]+)/?$', views.warehouse_stock_detail_view),
    re_path(r'^/stocks/?$', views.get_warehouse_stock_view),
    re_path(r'^/stock/(?P<id>[^/]+)/update/?$', views.warehouse_stock_detail_view),
    re_path(r'^/stock/(?P<id>[^/]+)/?$', views.warehouse_stock_detail_view),
    re_path(r'^/stock/?$', views.get_warehouse_stock_view),
]
