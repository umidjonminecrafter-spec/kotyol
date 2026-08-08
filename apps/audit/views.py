from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.response import Response
from django.db.models import Q
from core.authentication import JWTAuthentication
from core.permissions import IsAuthenticated, require_roles
from apps.audit.models import AuditLog
from apps.audit.serializers import AuditLogResponseSerializer


@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated, require_roles('ADMIN')])
def list_audit_logs_view(request):
    page = int(request.query_params.get('page', 1))
    limit = int(request.query_params.get('limit', 50))
    action = request.query_params.get('action')
    entity_name = request.query_params.get('entity_name')
    search = request.query_params.get('search')
    start_date = request.query_params.get('start_date')
    end_date = request.query_params.get('end_date')

    qs = AuditLog.objects.select_related('actor').all()
    if action:
        qs = qs.filter(action__icontains=action)
    if entity_name:
        qs = qs.filter(entity_name__icontains=entity_name)
    if search:
        qs = qs.filter(
            Q(entity_id__icontains=search) |
            Q(entity_name__icontains=search) |
            Q(action__icontains=search) |
            Q(actor__first_name__icontains=search) |
            Q(actor__last_name__icontains=search) |
            Q(actor__username__icontains=search)
        )
    if start_date:
        qs = qs.filter(created_at__date__gte=start_date)
    if end_date:
        qs = qs.filter(created_at__date__lte=end_date)

    total = qs.count()
    skip = (page - 1) * limit
    items = list(qs.order_by('-created_at')[skip:skip + limit])

    resp = AuditLogResponseSerializer(items, many=True).data
    total_pages = (total + limit - 1) // limit if limit > 0 else 1

    return Response({
        "success": True,
        "data": resp,
        "pagination": {"total": total, "page": page, "limit": limit, "total_pages": total_pages}
    })


@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated, require_roles('ADMIN')])
def get_audit_log_detail_view(request, log_id):
    try:
        log = AuditLog.objects.select_related('actor').get(id=log_id)
    except AuditLog.DoesNotExist:
        return Response({"success": False, "message": "Audit yozuvi topilmadi"}, status=404)
    return Response({"success": True, "data": AuditLogResponseSerializer(log).data})

