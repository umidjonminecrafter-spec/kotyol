import uuid
import json
from django.db.models import Sum, Count
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.response import Response
from rest_framework import status

from core.authentication import JWTAuthentication
from core.permissions import IsAuthenticated
from core.exceptions import CustomAppException
from core.audit_helper import record_audit_log
from apps.accounts.models import User, Branch, Organization, Position
from apps.accounts.serializers import (
    LoginRequestSerializer, RegisterRequestSerializer, UserCreateSerializer,
    UserInfoSerializer, RefreshRequestSerializer, BranchCreateSerializer,
    BranchResponseSerializer, PositionCreateSerializer, PositionResponseSerializer,
)
from apps.accounts.services import AuthService


def _user_info(user):
    return UserInfoSerializer(user).data


@api_view(['POST'])
def register_view(request):
    serializer = RegisterRequestSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user = AuthService.register_user(serializer.validated_data, request=request)
    return Response({'success': True, 'data': _user_info(user)})


@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def list_employees_view(request):
    users = AuthService.list_employees(request.user)
    return Response({'success': True, 'data': [_user_info(u) for u in users]})


@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def create_employee_view(request):
    serializer = UserCreateSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user = AuthService.create_employee_user(serializer.validated_data, request.user)
    return Response({'success': True, 'data': _user_info(user)})


@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def employee_detail_view(request, id):
    user = AuthService.get_employee_by_id(id)

    if request.method == 'GET':
        return Response({'success': True, 'data': _user_info(user)})

    if request.method in ['PUT', 'PATCH']:
        updated_user = AuthService.update_employee_user(id, request.data)
        record_audit_log(
            action="UPDATE",
            entity_name="USER",
            entity_id=id,
            actor_id=request.user.id,
            new_values=request.data,
            request=request
        )
        return Response({'success': True, 'data': _user_info(updated_user)})

    # DELETE
    AuthService.delete_employee_user(id)
    record_audit_log(
        action="DELETE",
        entity_name="USER",
        entity_id=id,
        actor_id=request.user.id,
        request=request
    )
    return Response({'success': True, 'message': "Xodim muvaffaqiyatli o'chirildi"})


@api_view(['POST'])
def login_view(request):
    serializer = LoginRequestSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    result = AuthService.authenticate_user(serializer.validated_data, request=request)
    return Response({
        'success': True,
        'data': {
            'access_token': result['access_token'],
            'refresh_token': result['refresh_token'],
            'token_type': result['token_type'],
            'user': _user_info(result['user']),
        },
    })


@api_view(['POST'])
def refresh_token_view(request):
    serializer = RefreshRequestSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    access_token = AuthService.refresh_access_token(serializer.validated_data['refresh_token'])
    return Response({'access_token': access_token, 'token_type': 'bearer'})


@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def get_me_view(request):
    user_info = _user_info(request.user)

    permissions_list = []
    if request.user.position and request.user.position.permissions:
        try:
            permissions_list = json.loads(request.user.position.permissions)
        except Exception:
            permissions_list = request.user.position.permissions.split(',')

    if not permissions_list:
        if request.user.role in ['ADMIN', 'SUPER_ADMIN']:
            permissions_list = ['*']
        elif request.user.role == 'PRODUCTION_OPERATOR':
            permissions_list = ['PRODUCTION_VIEW', 'PRODUCTION_EDIT']
        elif request.user.role == 'WAREHOUSE_KEEPER':
            permissions_list = ['WAREHOUSE_VIEW', 'WAREHOUSE_EDIT']
        else:
            permissions_list = ['PRODUCTION_VIEW', 'WAREHOUSE_VIEW', 'SALES_VIEW']

    return Response({'user': user_info, 'permissions': permissions_list})


# Branch management views

@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def list_branches_view(request):
    if not request.user.organization_id:
        return Response({'success': True, 'data': []})
    branches = Branch.objects.filter(organization_id=request.user.organization_id)
    return Response({'success': True, 'data': BranchResponseSerializer(branches, many=True).data})


@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def create_branch_view(request):
    if not request.user.organization_id:
        raise CustomAppException(message='Foydalanuvchi tashkilotga biriktirilmagan', status_code=400)
    serializer = BranchCreateSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    d = serializer.validated_data
    branch = Branch.objects.create(
        organization_id=request.user.organization_id,
        name=d['name'],
        code=d['code'],
        address=d.get('address'),
        phone=d.get('phone'),
    )
    return Response({'success': True, 'data': BranchResponseSerializer(branch).data})


@api_view(['PUT'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def update_branch_view(request, id):
    try:
        branch = Branch.objects.get(id=id, organization_id=request.user.organization_id)
    except Branch.DoesNotExist:
        raise CustomAppException(message='Filial topilmadi', status_code=404)
    serializer = BranchCreateSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    d = serializer.validated_data
    branch.name = d['name']
    branch.code = d['code']
    branch.address = d.get('address')
    branch.phone = d.get('phone')
    branch.save()
    return Response({'success': True, 'data': BranchResponseSerializer(branch).data})


@api_view(['DELETE'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def delete_branch_view(request, id):
    try:
        branch = Branch.objects.get(id=id, organization_id=request.user.organization_id)
    except Branch.DoesNotExist:
        raise CustomAppException(message='Filial topilmadi', status_code=404)
    branch.status = 'ARCHIVED'
    branch.save()
    return Response({'success': True, 'message': 'Filial muvaffaqiyatli arxivlandi'})


@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def get_branch_stats_view(request):
    from apps.sales.models import Sale
    from apps.production.models import ProductionBatch
    from apps.warehouse.models import WarehouseStock

    if not request.user.organization_id:
        return Response({'success': True, 'data': []})

    branches = Branch.objects.filter(organization_id=request.user.organization_id, status='ACTIVE')
    stats = []
    for b in branches:
        sales_rev = Sale.objects.filter(branch_id=b.id).aggregate(total=Sum('total_amount'))['total'] or 0
        sales_cnt = Sale.objects.filter(branch_id=b.id).count()
        prod_cnt = ProductionBatch.objects.filter(branch_id=b.id).aggregate(total=Sum('completed_quantity'))['total'] or 0
        stock_cnt = WarehouseStock.objects.filter(branch_id=b.id).aggregate(total=Sum('quantity'))['total'] or 0

        stats.append({
            'id': b.id,
            'name': b.name,
            'code': b.code,
            'revenue': float(sales_rev),
            'salesCount': int(sales_cnt),
            'productionVolume': int(prod_cnt),
            'stockVolume': float(stock_cnt),
        })

    return Response({'success': True, 'data': stats})


# Position CRUD views

@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def list_positions_view(request):
    positions = Position.objects.exclude(status='ARCHIVED')
    return Response({'success': True, 'data': PositionResponseSerializer(positions, many=True).data})


@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def create_position_view(request):
    serializer = PositionCreateSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    d = serializer.validated_data
    code = d['name'].strip().upper().replace(' ', '-')
    position = Position.objects.create(
        code=f"{code}-{str(uuid.uuid4())[:4]}",
        name=d['name'],
        description=d.get('description'),
        permissions=d.get('permissions'),
        status='ACTIVE',
    )
    return Response({
        'success': True,
        'data': PositionResponseSerializer(position).data,
        'message': 'Yangi lavozim muvaffaqiyatli saqlandi.',
    })


@api_view(['PUT'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def update_position_view(request, id):
    try:
        position = Position.objects.get(id=id)
    except Position.DoesNotExist:
        raise CustomAppException(message='Lavozim topilmadi', status_code=404)
    serializer = PositionCreateSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    d = serializer.validated_data
    position.name = d['name']
    position.description = d.get('description')
    if d.get('permissions') is not None:
        position.permissions = d['permissions']
    position.save()
    return Response({
        'success': True,
        'data': PositionResponseSerializer(position).data,
        'message': 'Lavozim muvaffaqiyatli tahrirlandi.',
    })


@api_view(['DELETE'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def delete_position_view(request, id):
    try:
        position = Position.objects.get(id=id)
    except Position.DoesNotExist:
        raise CustomAppException(message='Lavozim topilmadi', status_code=404)
    position.status = 'ARCHIVED'
    position.save()
    return Response({'success': True, 'message': "Lavozim muvaffaqiyatli o'chirildi."})
