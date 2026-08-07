from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.response import Response
from core.authentication import JWTAuthentication
from core.permissions import IsAuthenticated, require_roles
from core.audit_helper import record_audit_log
from apps.purchasing.services import PurchaseService
from apps.purchasing.serializers import PurchaseCreateSerializer, PurchaseUpdateStatusSerializer, PurchaseResponseSerializer

@api_view(['GET', 'POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def purchases_list_create_view(request):
    if request.method == 'GET':
        page = int(request.query_params.get('page', 1))
        limit = int(request.query_params.get('limit', 20))
        status_filter = request.query_params.get('status')

        items, total = PurchaseService.get_multi(page=page, limit=limit, status=status_filter)
        total_pages = (total + limit - 1) // limit if limit > 0 else 1

        response_items = PurchaseResponseSerializer(items, many=True).data

        return Response({
            "success": True,
            "data": response_items,
            "pagination": {"total": total, "page": page, "limit": limit, "total_pages": total_pages}
        })

    # POST (create)
    if request.user.role not in ["ADMIN", "MANAGER", "ACCOUNTANT", "WAREHOUSE_KEEPER"]:
        return Response({"success": False, "error_code": "FORBIDDEN", "message": "Ruxsat etilmagan"}, status=403)

    serializer = PurchaseCreateSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    body_data = serializer.validated_data

    p = PurchaseService.create_purchase(body_data, created_by_id=request.user.id)
    record_audit_log(
        action="CREATE",
        entity_name="PURCHASE",
        entity_id=p.id,
        actor_id=request.user.id,
        new_values=body_data,
        request=request
    )
    return Response({"success": True, "data": PurchaseResponseSerializer(p).data}, status=201)

@api_view(['PUT'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def update_purchase_status_view(request, id):
    if request.user.role not in ["ADMIN", "MANAGER", "ACCOUNTANT", "WAREHOUSE_KEEPER"]:
        return Response({"success": False, "error_code": "FORBIDDEN", "message": "Ruxsat etilmagan"}, status=403)

    serializer = PurchaseUpdateStatusSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    new_status = serializer.validated_data["status"]

    p = PurchaseService.update_status(id, new_status, updated_by_id=request.user.id)
    record_audit_log(
        action="UPDATE_STATUS",
        entity_name="PURCHASE",
        entity_id=id,
        actor_id=request.user.id,
        new_values={"status": new_status},
        request=request
    )
    return Response({"success": True, "data": PurchaseResponseSerializer(p).data})


@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def purchase_detail_view(request, id):
    from apps.purchasing.models import Purchase
    try:
        purchase = Purchase.objects.get(id=id)
    except Purchase.DoesNotExist:
        return Response({"success": False, "message": "Xarid topilmadi"}, status=404)

    if request.method == 'GET':
        return Response({"success": True, "data": PurchaseResponseSerializer(purchase).data})

    if request.method in ['PUT', 'PATCH']:
        serializer = PurchaseCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        body_data = serializer.validated_data
        skip_fields = {'items', 'supplier_name', 'notes', 'supplier_id', 'warehouse_id'}
        for k, v in body_data.items():
            if k in skip_fields:
                continue
            if hasattr(purchase, k) and v is not None:
                setattr(purchase, k, v)

        if body_data.get('supplier_id'):
            from apps.master_data.models import Supplier
            if Supplier.objects.filter(id=body_data['supplier_id']).exists():
                purchase.supplier_id = body_data['supplier_id']

        if body_data.get('warehouse_id'):
            from apps.master_data.models import Warehouse
            if Warehouse.objects.filter(id=body_data['warehouse_id']).exists():
                purchase.warehouse_id = body_data['warehouse_id']

        if body_data.get('notes') and hasattr(purchase, 'notes'):
            purchase.notes = body_data['notes']

        purchase.save()
        record_audit_log(
            action="UPDATE", entity_name="PURCHASE",
            entity_id=id, actor_id=request.user.id, new_values=body_data, request=request
        )
        return Response({"success": True, "data": PurchaseResponseSerializer(purchase).data})

    # DELETE
    purchase.delete()
    record_audit_log(
        action="DELETE", entity_name="PURCHASE",
        entity_id=id, actor_id=request.user.id, request=request
    )
    return Response({"success": True, "data": {"id": id, "deleted": True}})

