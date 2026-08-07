import uuid
from decimal import Decimal
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.response import Response
from core.authentication import JWTAuthentication
from core.permissions import IsAuthenticated
from core.audit_helper import record_audit_log
from core.exceptions import CustomAppException
from apps.warehouse.models import WarehouseStock
from apps.warehouse.services import WarehouseService
from apps.warehouse.serializers import StockResponseSerializer, StockAdjustmentRequestSerializer
from apps.master_data.models import Warehouse, ProductCategory, MaterialType, Unit
from apps.products.models import Product

@api_view(['GET', 'POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def get_warehouse_stock_view(request):
    if request.method == 'GET':
        warehouse_id = request.query_params.get('warehouse_id')
        product_id = request.query_params.get('product_id')
        page = int(request.query_params.get('page', 1))
        limit = int(request.query_params.get('limit', 20))

        items, total = WarehouseService.get_stocks(
            warehouse_id=warehouse_id, product_id=product_id, page=page, limit=limit
        )
        total_pages = (total + limit - 1) // limit if limit > 0 else 1

        response_items = StockResponseSerializer(items, many=True).data

        return Response({
            "success": True,
            "data": response_items,
            "pagination": {
                "total": total,
                "page": page,
                "limit": limit,
                "total_pages": total_pages
            }
        })

    # POST (Create / Adjust stock entry)
    serializer = StockAdjustmentRequestSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    d = serializer.validated_data

    warehouse_id = (d.get('warehouse_id') or "").strip()
    product_id = (d.get('product_id') or "").strip()

    # 1. Resolve or fallback Warehouse
    wh = None
    if warehouse_id:
        wh = Warehouse.objects.filter(id=warehouse_id).first()
    if not wh:
        wh = Warehouse.objects.first()
    if not wh:
        wh = Warehouse.objects.create(code="WH-MAIN", name="Asosiy Ombor")
    final_warehouse_id = wh.id

    # 2. Resolve or auto-create Product if product_id is missing or not found
    prod = None
    if product_id:
        prod = Product.objects.filter(id=product_id).first()

    p_code = (d.get('product_code') or d.get('code') or "").strip()
    p_name = (d.get('product_name') or d.get('name') or "").strip()

    if not prod and p_code:
        prod = Product.objects.filter(code=p_code).first()

    if not prod and p_name:
        prod = Product.objects.filter(name=p_name).first()

    if not prod:
        cat = ProductCategory.objects.first()
        if not cat:
            cat = ProductCategory.objects.create(code="CAT-MAIN", name="Asosiy Kategoriya")

        mt = MaterialType.objects.first()
        if not mt:
            mt = MaterialType.objects.create(code="MAT-STD", name="Standart Material")

        unit = Unit.objects.first()
        if not unit:
            unit = Unit.objects.create(code="UNIT-PCS", name="dona", symbol="dona")

        if not p_code:
            p_code = f"PRD-{str(uuid.uuid4())[:6]}"
        if not p_name:
            p_name = f"Mahsulot {p_code}"

        prod = Product.objects.create(
            code=p_code,
            name=p_name,
            category=cat,
            material_type=mt,
            unit=unit,
            type="RAW_MATERIAL",
            unit_price=Decimal(str(d.get('unit_cost') or 0.0))
        )
    final_product_id = prod.id

    # 3. Calculate quantity delta
    delta = d.get('quantity_delta')
    if delta is None or delta == 0.0:
        delta = d.get('quantity', 0.0) or 0.0

    unit_cost = Decimal(str(d.get('unit_cost') or 0.0))
    movement_type = d.get('movement_type') or "ADJUSTMENT"

    stock = WarehouseService.adjust_stock(
        warehouse_id=final_warehouse_id,
        product_id=final_product_id,
        quantity_delta=Decimal(str(delta)),
        unit_cost=unit_cost,
        movement_type=movement_type,
        notes=d.get('notes')
    )

    record_audit_log(
        action="ADJUST_STOCK",
        entity_name="WAREHOUSE_STOCK",
        entity_id=stock.id,
        actor_id=request.user.id,
        new_values=d,
        request=request
    )

    return Response({"success": True, "data": StockResponseSerializer(stock).data}, status=201)

@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def warehouse_stock_detail_view(request, id):
    try:
        stock = WarehouseStock.objects.get(id=id)
    except WarehouseStock.DoesNotExist:
        raise CustomAppException(message="Ombor qoldig'i topilmadi", status_code=404)

    if request.method == 'GET':
        return Response({"success": True, "data": StockResponseSerializer(stock).data})

    if request.method in ['PUT', 'PATCH']:
        serializer = StockAdjustmentRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        d = serializer.validated_data

        updated_stock = WarehouseService.update_stock(id, d, updated_by_id=request.user.id)

        record_audit_log(
            action="UPDATE_STOCK",
            entity_name="WAREHOUSE_STOCK",
            entity_id=id,
            actor_id=request.user.id,
            new_values=d,
            request=request
        )

        return Response({"success": True, "data": StockResponseSerializer(updated_stock).data})

    # DELETE
    stock.delete()
    record_audit_log(
        action="DELETE_STOCK",
        entity_name="WAREHOUSE_STOCK",
        entity_id=id,
        actor_id=request.user.id,
        request=request
    )
    return Response({"success": True, "data": {"id": id, "deleted": True}})
