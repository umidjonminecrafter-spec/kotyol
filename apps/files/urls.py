from django.urls import re_path
from apps.files import views

urlpatterns = [
    re_path(r'^/upload/?$', views.upload_file_view),
]
