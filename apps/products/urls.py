from django.urls import re_path
from apps.products import views

urlpatterns = [
    re_path(r'^/boilers/create/?$', views.boilers_list_create_view),
    re_path(r'^/boilers/(?P<id>[^/]+)/delete/?$', views.boiler_detail_view),
    re_path(r'^/boilers/(?P<id>[^/]+)/update/?$', views.boiler_detail_view),
    re_path(r'^/boilers/(?P<id>[^/]+)/?$', views.boiler_detail_view),
    re_path(r'^/boilers/?$', views.boilers_list_create_view),
    re_path(r'^/recipes/(?P<id>[^/]+)/?$', views.recipe_detail_view),
    re_path(r'^/recipes/?$', views.recipes_list_create_view),
    re_path(r'^/list/?$', views.products_list_create_view),
    re_path(r'^/create/?$', views.products_list_create_view),
    re_path(r'^/(?P<id>[^/]+)/?$', views.product_detail_view),
    re_path(r'^/?$', views.products_list_create_view),
]
