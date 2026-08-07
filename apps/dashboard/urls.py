from django.urls import re_path
from apps.dashboard import views

urlpatterns = [
    re_path(r'^/summary/?$', views.get_summary_view),
    re_path(r'^/charts/?$', views.get_charts_view),
]
