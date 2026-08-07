from django.urls import re_path
from apps.sales import views

urlpatterns = [
    re_path(r'^/create/?$', views.sales_list_create_view),
    re_path(r'^/list/?$', views.sales_list_create_view),
    re_path(r'^/(?P<id>[^/]+)/delete/?$', views.sale_detail_view),
    re_path(r'^/(?P<id>[^/]+)/?$', views.sale_detail_view),
    re_path(r'^/?$', views.sales_list_create_view),
]
