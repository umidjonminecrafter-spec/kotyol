from django.urls import re_path
from apps.finance import views

urlpatterns = [
    re_path(r'^/transactions/(?P<id>[^/]+)/delete/?$', views.transaction_detail_view),
    re_path(r'^/transactions/(?P<id>[^/]+)/?$', views.transaction_detail_view),
    re_path(r'^/transactions/?$', views.financial_transactions_view),
]
