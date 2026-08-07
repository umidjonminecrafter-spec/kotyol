import time
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.response import Response
from core.authentication import JWTAuthentication
from core.permissions import IsAuthenticated

_START_TIME = time.time()

@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def notifications_list_view(request):
    # Dynamic sample notifications
    sample_notifications = [
        {
            "id": "notif-1",
            "title": "Yangilangan ombor zaxirasi",
            "message": "Omborda 'Sinov Mahsulot 99' minimal darajadan pastga tushdi.",
            "type": "WARNING",
            "read": False,
            "created_at": "2026-07-31T10:00:00Z"
        },
        {
            "id": "notif-2",
            "title": "Yangi Ish Buyurtmasi",
            "message": "BATCH-890212 ishlab chiqarishga o'tkazildi.",
            "type": "INFO",
            "read": True,
            "created_at": "2026-07-31T09:30:00Z"
        },
        {
            "id": "notif-3",
            "title": "Sotuv Bajarildi",
            "message": "ORD-2026-1001 buyurtmasi to'lov qilindi.",
            "type": "SUCCESS",
            "read": True,
            "created_at": "2026-07-31T08:15:00Z"
        }
    ]
    return Response({
        "success": True,
        "data": sample_notifications
    })

@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def system_status_view(request):
    uptime = int(time.time() - _START_TIME)
    return Response({
        "success": True,
        "data": {
            "status": "OPERATIONAL",
            "server": "ONLINE",
            "database": "CONNECTED",
            "uptime_seconds": uptime,
            "version": "v1.5.0",
            "services": {
                "api": "ONLINE",
                "auth": "ONLINE",
                "database": "ONLINE",
                "storage": "ONLINE"
            }
        }
    })
