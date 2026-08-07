from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.response import Response
from core.authentication import JWTAuthentication
from core.permissions import IsAuthenticated, require_roles
from core.audit_helper import record_audit_log
from core.exceptions import CustomAppException
from apps.master_data.models import Company
from apps.master_data.services import MasterDataService
from apps.master_data.serializers import (
    MasterDataCreateSerializer, MasterDataUpdateSerializer, MasterDataResponseSerializer,
    CompanyUpdateSerializer, CompanyResponseSerializer
)

@api_view(['GET', 'POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def master_data_list_create_view(request, entity_key):
    if request.method == 'GET':
        include_archived = request.query_params.get('include_archived', 'false').lower() == 'true'
        items, total = MasterDataService.get_multi(entity_key, include_archived=include_archived)
        resp = MasterDataResponseSerializer(items, many=True).data
        return Response({"success": True, "data": resp})

    # POST (create)
    serializer = MasterDataCreateSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    body_data = serializer.validated_data
    item = MasterDataService.create(entity_key, body_data, created_by_id=request.user.id)
    record_audit_log(
        action="CREATE",
        entity_name=entity_key.upper(),
        entity_id=item.id,
        actor_id=request.user.id,
        new_values=body_data,
        request=request
    )
    return Response({"success": True, "data": MasterDataResponseSerializer(item).data}, status=201)

@api_view(['GET', 'PUT', 'DELETE'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def master_data_detail_view(request, entity_key, id):
    model = MasterDataService.get_model(entity_key)
    try:
        item = model.objects.get(id=id)
    except model.DoesNotExist:
        raise CustomAppException(message="Master data topilmadi", status_code=404)

    if request.method == 'GET':
        return Response({"success": True, "data": MasterDataResponseSerializer(item).data})

    if request.method == 'PUT':
        serializer = MasterDataUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        body_data = {k: v for k, v in serializer.validated_data.items() if v is not None}
        updated_item = MasterDataService.update(entity_key, id, body_data, updated_by_id=request.user.id)
        record_audit_log(
            action="UPDATE",
            entity_name=entity_key.upper(),
            entity_id=id,
            actor_id=request.user.id,
            new_values=body_data,
            request=request
        )
        return Response({"success": True, "data": MasterDataResponseSerializer(updated_item).data})

    # DELETE
    MasterDataService.delete(entity_key, id)
    record_audit_log(
        action="DELETE",
        entity_name=entity_key.upper(),
        entity_id=id,
        actor_id=request.user.id,
        request=request
    )
    return Response({"success": True, "data": {"id": id, "deleted": True}})

@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def archive_master_data_view(request, entity_key, id):
    item = MasterDataService.archive(entity_key, id, updated_by_id=request.user.id)
    record_audit_log(
        action="ARCHIVE",
        entity_name=entity_key.upper(),
        entity_id=id,
        actor_id=request.user.id,
        request=request
    )
    return Response({"success": True, "data": MasterDataResponseSerializer(item).data})

@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def restore_master_data_view(request, entity_key, id):
    item = MasterDataService.restore(entity_key, id, updated_by_id=request.user.id)
    record_audit_log(
        action="RESTORE",
        entity_name=entity_key.upper(),
        entity_id=id,
        actor_id=request.user.id,
        request=request
    )
    return Response({"success": True, "data": MasterDataResponseSerializer(item).data})

@api_view(['GET', 'PUT'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def company_profile_view(request):
    company = Company.objects.first()
    if not company:
        company = Company.objects.create(
            name=request.user.organization_name or "Kotyol Manufacturing",
            phone=request.user.phone or "+998 (90) 123-45-67",
            website="https://kotyol.uz",
            address="Toshkent sh., Chilonzor tumani, 5-daha",
            description="Yuqori sifatli isitish kotyollari ishlab chiqarish zavodi.",
            currency="UZS",
            timezone="Asia/Tashkent (UTC+5)",
            date_format="YYYY-MM-DD"
        )
    else:
        modified = False
        if (company.name == "UZS Korxona" or not company.name) and request.user.organization_name:
            company.name = request.user.organization_name
            modified = True
        if (company.phone == "+99898546757" or not company.phone) and request.user.phone:
            company.phone = request.user.phone
            modified = True
        if modified:
            company.save()

    if request.method == 'GET':
        return Response({"success": True, "data": CompanyResponseSerializer(company).data})

    # PUT
    serializer = CompanyUpdateSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    update_data = {k: v for k, v in serializer.validated_data.items() if v is not None}
    for key, value in update_data.items():
        setattr(company, key, value)
    company.save()

    # Also sync updated name/phone to user's registered organization details
    if "name" in update_data and update_data["name"] and request.user.organization_name != update_data["name"]:
        request.user.organization_name = update_data["name"]
        if request.user.organization_id_fk:
            request.user.organization_id_fk.name = update_data["name"]
            request.user.organization_id_fk.save()
        request.user.save()

    record_audit_log(
        action="UPDATE",
        entity_name="COMPANY_PROFILE",
        entity_id=company.id,
        actor_id=request.user.id,
        new_values=update_data,
        request=request
    )
    return Response({"success": True, "data": CompanyResponseSerializer(company).data})


@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def complete_service_ticket_view(request, id):
    from apps.master_data.models import ServiceTicket
    from apps.finance.models import FinancialTransaction
    from apps.master_data.models import ExpenseType
    from apps.accounts.models import User
    import decimal
    import datetime
    import uuid

    try:
        ticket = ServiceTicket.objects.get(id=id)
    except ServiceTicket.DoesNotExist:
        raise CustomAppException(message="Servis topilmadi", status_code=404)

    service_cost = decimal.Decimal(str(request.data.get('service_cost', 0.0) or 0.0))
    employee_cost = decimal.Decimal(str(request.data.get('employee_cost', 0.0) or 0.0))

    ticket.service_cost = service_cost
    ticket.employee_cost = employee_cost
    ticket.status = "COMPLETED"
    ticket.save()

    # Generate Income transaction
    if service_cost > 0:
        FinancialTransaction.objects.create(
            transaction_number=f"SRV-REV-{datetime.datetime.now().strftime('%y%m%d%H%M%S')}-{str(uuid.uuid4())[:4].upper()}",
            type="INCOME",
            amount=service_cost,
            currency="USD",
            reference_id=str(ticket.id),
            transaction_date=datetime.date.today(),
            notes=f"Servis xizmati daromadi (Servis №{ticket.service_number}): {ticket.customer_name or 'Mijoz'}"
        )

    # Generate Expense transaction & add to employee salary
    if employee_cost > 0 and ticket.assigned_employee_id:
        salary_exp_type, _ = ExpenseType.objects.get_or_create(
            code="salary",
            defaults={"name": "Ish haqi xarajatlari"}
        )
        FinancialTransaction.objects.create(
            transaction_number=f"SAL-SRV-{datetime.datetime.now().strftime('%y%m%d%H%M%S')}-{str(uuid.uuid4())[:4].upper()}",
            type="EXPENSE",
            expense_type=salary_exp_type,
            amount=employee_cost,
            currency="USD",
            reference_id=str(ticket.id),
            transaction_date=datetime.date.today(),
            notes=f"Xodim servis ulushi (Servis №{ticket.service_number}): {ticket.assigned_employee_name or 'Xodim'}"
        )

        try:
            emp = User.objects.get(id=ticket.assigned_employee_id)
            curr = 0.0
            if emp.salary_amount:
                try:
                    curr = float(emp.salary_amount)
                except ValueError:
                    pass
            emp.salary_amount = str(curr + float(employee_cost))
            emp.save()
        except User.DoesNotExist:
            pass

    return Response({
        "success": True, 
        "message": "Servis muvaffaqiyatli yakunlandi, daromadlar va xodim maoshi yangilandi!",
        "data": MasterDataResponseSerializer(ticket).data
    })
