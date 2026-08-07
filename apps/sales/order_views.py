from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.response import Response
from core.authentication import JWTAuthentication
from core.permissions import IsAuthenticated
from core.audit_helper import record_audit_log
from apps.sales.order_services import OrderService
from apps.sales.order_serializers import OrderCreateSerializer, OrderResponseSerializer

@api_view(['GET', 'POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def orders_list_create_view(request):
    if request.method == 'GET':
        page = int(request.query_params.get('page', 1))
        limit = int(request.query_params.get('limit', 20))
        search = request.query_params.get('search')
        status = request.query_params.get('status')
        priority = request.query_params.get('priority')
        customer_id = request.query_params.get('customerId') or request.query_params.get('customer_id')

        items, total = OrderService.get_multi(
            page=page, limit=limit, search=search, status=status, priority=priority, customer_id=customer_id
        )
        total_pages = (total + limit - 1) // limit if limit > 0 else 1

        return Response({
            "success": True,
            "data": OrderResponseSerializer(items, many=True).data,
            "pagination": {"total": total, "page": page, "limit": limit, "total_pages": total_pages}
        })

    # POST (create)
    serializer = OrderCreateSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    body_data = serializer.validated_data

    order = OrderService.create_order(body_data, created_by_id=request.user.id)
    record_audit_log(
        action="CREATE",
        entity_name="ORDER",
        entity_id=order.id,
        actor_id=request.user.id,
        new_values=body_data,
        request=request
    )
    return Response({"success": True, "data": OrderResponseSerializer(order).data}, status=201)


@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def order_detail_view(request, id):
    if request.method == 'GET':
        order = OrderService.get_by_id(id)
        return Response({"success": True, "data": OrderResponseSerializer(order).data})

    if request.method in ['PUT', 'PATCH']:
        serializer = OrderCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        body_data = serializer.validated_data

        updated_order = OrderService.update_order(id, body_data, updated_by_id=request.user.id)
        record_audit_log(
            action="UPDATE",
            entity_name="ORDER",
            entity_id=id,
            actor_id=request.user.id,
            new_values=body_data,
            request=request
        )
        return Response({"success": True, "data": OrderResponseSerializer(updated_order).data})

    # DELETE
    OrderService.delete_order(id)
    record_audit_log(
        action="DELETE",
        entity_name="ORDER",
        entity_id=id,
        actor_id=request.user.id,
        request=request
    )
    return Response({"success": True, "data": {"id": id, "deleted": True}})


@api_view(['PUT', 'POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def start_order_production_view(request, id):
    res = OrderService.start_production(id, updated_by_id=request.user.id)
    record_audit_log(
        action="START_PRODUCTION",
        entity_name="ORDER",
        entity_id=id,
        actor_id=request.user.id,
        new_values={"status": "IN_PRODUCTION", "batch_id": res.get("batch_id")},
        request=request
    )
    return Response({
        "success": True,
        "message": "Ishlab chiqarish jarayoni boshlandi",
        "data": {
            "order": OrderResponseSerializer(res["order"]).data,
            "batch_id": res.get("batch_id"),
            "batch_number": res.get("batch_number")
        }
    })
