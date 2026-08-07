from django.urls import re_path
from apps.master_data import views
from apps.products.views import boilers_list_create_view, boiler_detail_view

urlpatterns = [
    re_path(r'^/company/profile/?$', views.company_profile_view),
    re_path(r'^/boilers/create/?$', boilers_list_create_view),
    re_path(r'^/boilers/(?P<id>[^/]+)/delete/?$', boiler_detail_view),
    re_path(r'^/boilers/(?P<id>[^/]+)/update/?$', boiler_detail_view),
    re_path(r'^/boilers/(?P<id>[^/]+)/?$', boiler_detail_view),
    re_path(r'^/boilers/?$', boilers_list_create_view),
    re_path(r'^/services/(?P<id>[^/]+)/complete/?$', views.complete_service_ticket_view),
    re_path(r'^/(?P<entity_key>[^/]+)/create/?$', views.master_data_list_create_view),
    re_path(r'^/(?P<entity_key>[^/]+)/(?P<id>[^/]+)/archive/?$', views.archive_master_data_view),
    re_path(r'^/(?P<entity_key>[^/]+)/(?P<id>[^/]+)/restore/?$', views.restore_master_data_view),
    re_path(r'^/(?P<entity_key>[^/]+)/(?P<id>[^/]+)/?$', views.master_data_detail_view),
    re_path(r'^/(?P<entity_key>[^/]+)/?$', views.master_data_list_create_view),
]
