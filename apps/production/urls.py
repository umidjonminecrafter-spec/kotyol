from django.urls import re_path
from apps.production import views

urlpatterns = [
    re_path(r'^/batches/create/?$', views.production_batches_list_create_view),
    re_path(r'^/batches/(?P<id>[^/]+)/delete/?$', views.production_batch_detail_view),
    re_path(r'^/batches/(?P<id>[^/]+)/update/?$', views.production_batch_detail_view),
    re_path(r'^/batches/(?P<id>[^/]+)/?$', views.production_batch_detail_view),
    re_path(r'^/batches/?$', views.production_batches_list_create_view),
    re_path(r'^/operations/(?P<op_id>[^/]+)/complete/?$', views.complete_operation_view),
]
