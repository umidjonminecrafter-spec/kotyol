from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.response import Response
from core.authentication import JWTAuthentication
from core.permissions import IsAuthenticated, require_roles
from core.audit_helper import record_audit_log
from apps.products.models import Boiler
from apps.products.services import ProductService, RecipeService, BoilerService
from apps.products.serializers import (
    ProductCreateSerializer, ProductUpdateSerializer, ProductResponseSerializer,
    RecipeCreateSerializer, RecipeResponseSerializer,
    BoilerCreateSerializer, BoilerResponseSerializer
)

@api_view(['GET', 'POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def products_list_create_view(request):
    if request.method == 'GET':
        page = int(request.query_params.get('page', 1))
        limit = int(request.query_params.get('limit', 20))
        search = request.query_params.get('search')
        category_id = request.query_params.get('category_id')
        product_type = request.query_params.get('type')
        status_filter = request.query_params.get('status', 'ACTIVE')

        items, total = ProductService.get_multi(
            page=page, limit=limit, search=search, category_id=category_id, product_type=product_type, status=status_filter
        )
        total_pages = (total + limit - 1) // limit if limit > 0 else 1
        
        response_items = ProductResponseSerializer(items, many=True).data

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

    # POST (create)
    if request.user.role not in ['ADMIN', 'MANAGER']:
        return Response({"success": False, "error_code": "FORBIDDEN", "message": "Ruxsat etilmagan"}, status=403)

    serializer = ProductCreateSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    body_data = serializer.validated_data

    product = ProductService.create(body_data, created_by_id=request.user.id)
    record_audit_log(
        action="CREATE",
        entity_name="PRODUCT",
        entity_id=product.id,
        actor_id=request.user.id,
        new_values=body_data,
        request=request
    )
    return Response({"success": True, "data": ProductResponseSerializer(product).data}, status=201)

@api_view(['GET', 'PUT', 'DELETE'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def product_detail_view(request, id):
    if request.method == 'GET':
        product = ProductService.get_by_id(id)
        return Response({"success": True, "data": ProductResponseSerializer(product).data})

    if request.method == 'PUT':
        if request.user.role not in ['ADMIN', 'MANAGER']:
            return Response({"success": False, "error_code": "FORBIDDEN", "message": "Ruxsat etilmagan"}, status=403)

        old_product = ProductService.get_by_id(id)
        old_values = {"name": old_product.name, "unit_price": float(old_product.unit_price)}

        serializer = ProductUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        update_data = {k: v for k, v in serializer.validated_data.items() if v is not None}

        updated = ProductService.update(id, update_data, updated_by_id=request.user.id)
        record_audit_log(
            action="UPDATE",
            entity_name="PRODUCT",
            entity_id=id,
            actor_id=request.user.id,
            old_values=old_values,
            new_values=update_data,
            request=request
        )
        return Response({"success": True, "data": ProductResponseSerializer(updated).data})

    # DELETE
    if request.user.role not in ['ADMIN']:
        return Response({"success": False, "error_code": "FORBIDDEN", "message": "Ruxsat etilmagan"}, status=403)

    ProductService.delete(id)
    record_audit_log(
        action="DELETE",
        entity_name="PRODUCT",
        entity_id=id,
        actor_id=request.user.id,
        request=request
    )
    return Response({"success": True, "data": {"id": id, "deleted": True}})


@api_view(['GET', 'POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def recipes_list_create_view(request):
    if request.method == 'GET':
        page = int(request.query_params.get('page', 1))
        limit = int(request.query_params.get('limit', 20))
        items, total = RecipeService.get_multi(page=page, limit=limit)
        total_pages = (total + limit - 1) // limit if limit > 0 else 1
        resp = RecipeResponseSerializer(items, many=True).data
        return Response({
            "success": True,
            "data": resp,
            "pagination": {"total": total, "page": page, "limit": limit, "total_pages": total_pages}
        })

    # POST
    serializer = RecipeCreateSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    body_data = serializer.validated_data
    recipe = RecipeService.create(body_data, created_by_id=request.user.id)
    record_audit_log(
        action="CREATE",
        entity_name="RECIPE",
        entity_id=recipe.id,
        actor_id=request.user.id,
        new_values=body_data,
        request=request
    )
    return Response({"success": True, "data": RecipeResponseSerializer(recipe).data}, status=201)


@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def recipe_detail_view(request, id):
    if request.method == 'GET':
        recipe = RecipeService.get_by_id(id)
        return Response({"success": True, "data": RecipeResponseSerializer(recipe).data})

    if request.method in ['PUT', 'PATCH']:
        serializer = RecipeCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        body_data = serializer.validated_data
        updated_recipe = RecipeService.update(id, body_data, updated_by_id=request.user.id)
        record_audit_log(
            action="UPDATE",
            entity_name="RECIPE",
            entity_id=id,
            actor_id=request.user.id,
            new_values=body_data,
            request=request
        )
        return Response({"success": True, "data": RecipeResponseSerializer(updated_recipe).data})

    # DELETE
    RecipeService.delete(id)
    record_audit_log(
        action="DELETE",
        entity_name="RECIPE",
        entity_id=id,
        actor_id=request.user.id,
        request=request
    )
    return Response({"success": True, "data": {"id": id, "deleted": True}})


@api_view(['GET', 'POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def boilers_list_create_view(request):
    if request.method == 'GET':
        items = BoilerService.get_multi()
        resp = BoilerResponseSerializer(items, many=True).data
        return Response({"success": True, "data": resp})

    # POST (create)
    serializer = BoilerCreateSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    body_data = serializer.validated_data
    boiler = BoilerService.create_boiler(body_data, created_by_id=request.user.id)
    record_audit_log(
        action="CREATE",
        entity_name="BOILER",
        entity_id=boiler.id,
        actor_id=request.user.id,
        new_values=body_data,
        request=request
    )
    return Response({"success": True, "data": BoilerResponseSerializer(boiler).data}, status=201)


@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def boiler_detail_view(request, id):
    try:
        boiler = Boiler.objects.get(id=id)
    except Boiler.DoesNotExist:
        from core.exceptions import CustomAppException
        raise CustomAppException(message="Kotyol modeli topilmadi", status_code=404)

    if request.method == 'GET':
        return Response({"success": True, "data": BoilerResponseSerializer(boiler).data})

    if request.method in ['PUT', 'PATCH']:
        serializer = BoilerCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        body_data = serializer.validated_data
        updated_boiler = BoilerService.update_boiler(id, body_data, updated_by_id=request.user.id)
        record_audit_log(
            action="UPDATE",
            entity_name="BOILER",
            entity_id=id,
            actor_id=request.user.id,
            new_values=body_data,
            request=request
        )
        return Response({"success": True, "data": BoilerResponseSerializer(updated_boiler).data})

    # DELETE
    BoilerService.delete_boiler(id)
    record_audit_log(
        action="DELETE",
        entity_name="BOILER",
        entity_id=id,
        actor_id=request.user.id,
        request=request
    )
    return Response({"success": True, "data": {"id": id, "deleted": True}})
