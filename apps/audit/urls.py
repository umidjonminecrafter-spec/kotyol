from django.urls import re_path
from apps.audit import views

urlpatterns = [
    re_path(r'^/?$', views.list_audit_logs_view),
    re_path(r'^/logs/?$', views.list_audit_logs_view),
    re_path(r'^/list/?$', views.list_audit_logs_view),
]
