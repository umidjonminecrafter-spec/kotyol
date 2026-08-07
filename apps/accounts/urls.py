from django.urls import re_path
from apps.accounts import views

urlpatterns = [
    re_path(r'^/login/?$', views.login_view),
    re_path(r'^/register/?$', views.register_view),
    re_path(r'^/employees/create/?$', views.create_employee_view),
    re_path(r'^/employees/(?P<id>[^/]+)/update/?$', views.employee_detail_view),
    re_path(r'^/employees/(?P<id>[^/]+)/delete/?$', views.employee_detail_view),
    re_path(r'^/employees/(?P<id>[^/]+)/?$', views.employee_detail_view),
    re_path(r'^/employees/?$', views.list_employees_view),
    re_path(r'^/refresh/?$', views.refresh_token_view),
    re_path(r'^/me/?$', views.get_me_view),
    re_path(r'^/branches/?$', views.list_branches_view),
    re_path(r'^/branches/create/?$', views.create_branch_view),
    re_path(r'^/branches/stats/?$', views.get_branch_stats_view),
    re_path(r'^/branches/(?P<id>[^/]+)/?$', views.update_branch_view),
    re_path(r'^/branches/(?P<id>[^/]+)/delete/?$', views.delete_branch_view),
    re_path(r'^/positions/?$', views.list_positions_view),
    re_path(r'^/positions/create/?$', views.create_position_view),
    re_path(r'^/positions/(?P<id>[^/]+)/?$', views.update_position_view),
    re_path(r'^/positions/(?P<id>[^/]+)/delete/?$', views.delete_position_view),
]
