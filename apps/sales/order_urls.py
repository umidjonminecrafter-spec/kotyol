from django.urls import re_path
from apps.sales import order_views as views

urlpatterns = [
    re_path(r'^/create/?$', views.orders_list_create_view),
    re_path(r'^/orders/create/?$', views.orders_list_create_view),
    re_path(r'^/orders/(?P<id>[^/]+)/start-production/?$', views.start_order_production_view),
    re_path(r'^/(?P<id>[^/]+)/start-production/?$', views.start_order_production_view),
    re_path(r'^/orders/(?P<id>[^/]+)/?$', views.order_detail_view),
    re_path(r'^/(?P<id>[^/]+)/delete/?$', views.order_detail_view),
    re_path(r'^/(?P<id>[^/]+)/?$', views.order_detail_view),
    re_path(r'^/orders/?$', views.orders_list_create_view),
    re_path(r'^/?$', views.orders_list_create_view),
]
