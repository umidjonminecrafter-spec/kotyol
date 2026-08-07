from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.response import Response
from core.authentication import JWTAuthentication
from core.permissions import IsAuthenticated
from core.audit_helper import record_audit_log
from core.exceptions import CustomAppException
from apps.production.models import ProductionBatch
from apps.production.services import ProductionService
from apps.production.serializers import ProductionBatchCreateSerializer, ProductionBatchUpdateSerializer, ProductionBatchResponseSerializer

@api_view(['GET', 'POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def production_batches_list_create_view(request):
    if request.method == 'GET':
        page = int(request.query_params.get('page', 1))
        limit = int(request.query_params.get('limit', 20))
        status_filter = request.query_params.get('status')

        items, total = ProductionService.get_multi(page=page, limit=limit, status=status_filter)
        total_pages = (total + limit - 1) // limit if limit > 0 else 1

        response_items = ProductionBatchResponseSerializer(items, many=True).data

        return Response({
            "success": True,
            "data": response_items,
            "pagination": {"total": total, "page": page, "limit": limit, "total_pages": total_pages}
        })

    # POST (create)
    if request.user.role not in ["ADMIN", "MANAGER", "TECHNICIAN"]:
        return Response({"success": False, "error_code": "FORBIDDEN", "message": "Ruxsat etilmagan"}, status=403)

    serializer = ProductionBatchCreateSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    body_data = serializer.validated_data

    batch = ProductionService.create_batch(body_data, created_by_id=request.user.id)
    record_audit_log(
        action="CREATE",
        entity_name="PRODUCTION_BATCH",
        entity_id=batch.id,
        actor_id=request.user.id,
        new_values=body_data,
        request=request
    )
    return Response({"success": True, "data": ProductionBatchResponseSerializer(batch).data}, status=201)

@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def production_batch_detail_view(request, id):
    try:
        batch = ProductionBatch.objects.get(id=id)
    except ProductionBatch.DoesNotExist:
        raise CustomAppException(message="Ishlab chiqarish partiyasi topilmadi", status_code=404)

    if request.method == 'GET':
        return Response({"success": True, "data": ProductionBatchResponseSerializer(batch).data})

    if request.user.role not in ["ADMIN", "MANAGER", "TECHNICIAN"]:
        return Response({"success": False, "error_code": "FORBIDDEN", "message": "Ruxsat etilmagan"}, status=403)

    if request.method in ['PUT', 'PATCH']:
        serializer = ProductionBatchUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        body_data = {k: v for k, v in serializer.validated_data.items() if v is not None}

        updated_batch = ProductionService.update_batch(id, body_data, updated_by_id=request.user.id)
        record_audit_log(
            action="UPDATE",
            entity_name="PRODUCTION_BATCH",
            entity_id=id,
            actor_id=request.user.id,
            new_values=body_data,
            request=request
        )
        return Response({"success": True, "data": ProductionBatchResponseSerializer(updated_batch).data})

    # DELETE
    ProductionService.delete_batch(id)
    record_audit_log(
        action="DELETE",
        entity_name="PRODUCTION_BATCH",
        entity_id=id,
        actor_id=request.user.id,
        request=request
    )
    return Response({"success": True, "data": {"id": id, "deleted": True}})

@api_view(['PUT'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def complete_operation_view(request, op_id):
    from apps.production.models import ProductionOperation
    try:
        op = ProductionOperation.objects.get(id=op_id)
    except ProductionOperation.DoesNotExist:
        raise CustomAppException(message="Operatsiya topilmadi", status_code=404)
        
    op.status = "COMPLETED"
    op.save()
    
    # Generate financial transaction for worker salary if rate > 0
    if op.rate > 0:
        from apps.finance.models import FinancialTransaction
        from apps.master_data.models import ExpenseType
        import datetime
        import uuid
        
        salary_exp_type, _ = ExpenseType.objects.get_or_create(
            code="salary",
            defaults={"name": "Ish haqi xarajatlari"}
        )
        
        FinancialTransaction.objects.create(
            transaction_number=f"SAL-OP-{datetime.datetime.now().strftime('%y%m%d%H%M%S')}-{str(uuid.uuid4())[:4].upper()}",
            type="EXPENSE",
            expense_type=salary_exp_type,
            amount=op.rate,
            currency="USD",
            reference_id=str(op.id),
            transaction_date=datetime.date.today(),
            notes=f"Usta ish haqi (Operatsiya yakunlandi): {op.worker_name or 'Usta'} — Operatsiya: {op.operation_name}"
        )
        
    return Response({"success": True, "message": "Operatsiya muvaffaqiyatli yakunlandi!"})
