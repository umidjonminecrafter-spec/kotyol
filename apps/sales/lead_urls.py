from django.urls import re_path
from apps.sales import lead_views

urlpatterns = [
    re_path(r'^/create/?$', lead_views.leads_list_create_view),
    re_path(r'^/list/?$', lead_views.leads_list_create_view),
    re_path(r'^/(?P<id>[^/]+)/delete/?$', lead_views.lead_detail_view),
    re_path(r'^/(?P<id>[^/]+)/?$', lead_views.lead_detail_view),
    re_path(r'^/?$', lead_views.leads_list_create_view),
]
