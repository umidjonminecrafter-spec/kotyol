from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import JsonResponse
from apps.dashboard.system_views import notifications_list_view, system_status_view


def health_check(request):
    return JsonResponse({
        'status': 'online',
        'app': settings.PROJECT_NAME,
        'environment': settings.ENVIRONMENT,
    })


urlpatterns = [
    path('admin/', admin.site.urls),
    path('health', health_check),
    path('api/v1/auth', include('apps.accounts.urls')),
    path('api/v1/dashboard', include('apps.dashboard.urls')),
    path('api/v1/products', include('apps.products.urls')),
    path('api/v1/master-data', include('apps.master_data.urls')),
    path('api/v1/warehouse', include('apps.warehouse.urls')),
    path('api/v1/purchasing', include('apps.purchasing.urls')),
    path('api/v1/production', include('apps.production.urls')),
    path('api/v1/sales', include('apps.sales.urls')),
    path('api/v1/orders', include('apps.sales.order_urls')),
    path('api/v1/leads', include('apps.sales.lead_urls')),
    path('api/v1/finance', include('apps.finance.urls')),
    path('api/v1/audit-logs', include('apps.audit.urls')),
    path('api/v1/files', include('apps.files.urls')),
    path('api/v1/reports', include('apps.dashboard.report_urls')),
    path('api/v1/notifications', notifications_list_view),
    path('api/v1/system/status', system_status_view),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
