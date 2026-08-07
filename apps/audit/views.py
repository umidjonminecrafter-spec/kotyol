from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.response import Response
from core.authentication import JWTAuthentication
from core.permissions import IsAuthenticated, require_roles
from apps.audit.models import AuditLog
from apps.audit.serializers import AuditLogResponseSerializer

@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated, require_roles('ADMIN')])
def list_audit_logs_view(request):
    page = int(request.query_params.get('page', 1))
    limit = int(request.query_params.get('limit', 20))
    action = request.query_params.get('action')
    entity_name = request.query_params.get('entity_name')

    qs = AuditLog.objects.all()
    if action:
        qs = qs.filter(action=action)
    if entity_name:
        qs = qs.filter(entity_name=entity_name)

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
