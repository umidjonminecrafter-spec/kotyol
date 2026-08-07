from django.urls import re_path
from apps.purchasing import views

urlpatterns = [
    re_path(r'^/create/?$', views.purchases_list_create_view),
    re_path(r'^/list/?$', views.purchases_list_create_view),
    re_path(r'^/orders/?$', views.purchases_list_create_view),
    re_path(r'^/(?P<id>[^/]+)/status/?$', views.update_purchase_status_view),
    re_path(r'^/(?P<id>[^/]+)/delete/?$', views.purchase_detail_view),
    re_path(r'^/(?P<id>[^/]+)/?$', views.purchase_detail_view),
    re_path(r'^/?$', views.purchases_list_create_view),
]
