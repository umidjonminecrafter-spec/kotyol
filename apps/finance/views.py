from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.response import Response
from core.authentication import JWTAuthentication
from core.permissions import IsAuthenticated, require_roles
from core.audit_helper import record_audit_log
from apps.finance.models import FinancialTransaction
from apps.finance.serializers import TransactionCreateSerializer, TransactionResponseSerializer

def resolve_expense_type_id(exp_type_id):
    if not exp_type_id or not str(exp_type_id).strip() or str(exp_type_id).strip() in ["undefined", "null"]:
        return None
    
    from apps.master_data.models import ExpenseType
    from django.db import models
    import uuid
    
    val = str(exp_type_id).strip()
    is_uuid = False
    try:
        uuid.UUID(val)
        is_uuid = True
    except ValueError:
        pass
        
    if is_uuid:
        obj = ExpenseType.objects.filter(id=val).first()
        if obj:
            return obj.id
            
    # Try finding by code or name
    obj = ExpenseType.objects.filter(
        models.Q(code__iexact=val) | models.Q(name__icontains=val)
    ).first()
    if obj:
        return obj.id
        
    # Auto-create
    code_val = val.upper()
    name_val = val.capitalize()
    if code_val == "SALARY":
        name_val = "Ish haqi"
    obj = ExpenseType.objects.create(code=code_val, name=name_val)
    return obj.id

@api_view(['GET', 'POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def financial_transactions_view(request):
    if request.method == 'GET':
        page = int(request.query_params.get('page', 1))
        limit = int(request.query_params.get('limit', 20))

        qs = FinancialTransaction.objects.all().order_by('-created_at')
        total = qs.count()
        skip = (page - 1) * limit
        items = list(qs[skip:skip + limit])

        resp = TransactionResponseSerializer(items, many=True).data
        return Response({"success": True, "data": resp})

    # POST (create)
    if request.user.role not in ['ADMIN', 'ACCOUNTANT']:
        return Response({"success": False, "error_code": "FORBIDDEN", "message": "Ruxsat etilmagan"}, status=403)

    serializer = TransactionCreateSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    body_data = serializer.validated_data

    import uuid
    import datetime

    t_num = (body_data.get("transaction_number") or "").strip()
    if not t_num or t_num in ["undefined", "null"]:
        t_num = f"TXN-{datetime.date.today().year}-{str(uuid.uuid4())[:6].upper()}"
    if FinancialTransaction.objects.filter(transaction_number=t_num).exists():
        t_num = f"TXN-{datetime.date.today().year}-{str(uuid.uuid4())[:6].upper()}"

    t_date = body_data.get("transaction_date")
    if not t_date:
        t_date = datetime.date.today()

    exp_type_id = resolve_expense_type_id(body_data.get("expense_type_id"))

    notes = body_data.get("notes") or body_data.get("description") or ""

    tx = FinancialTransaction.objects.create(
        transaction_number=t_num,
        type=body_data.get("type") or "INCOME",
        expense_type_id=exp_type_id,
        amount=body_data.get("amount") or 0,
        currency=body_data.get("currency") or "USD",
        reference_id=body_data.get("reference_id") or None,
        transaction_date=t_date,
        notes=notes,
        created_by_id=request.user.id
    )

    record_audit_log(
        action="CREATE",
        entity_name="FINANCIAL_TRANSACTION",
        entity_id=tx.id,
        actor_id=request.user.id,
        new_values=body_data,
        request=request
    )
    return Response({"success": True, "data": TransactionResponseSerializer(tx).data}, status=201)


@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def transaction_detail_view(request, id):
    try:
        tx = FinancialTransaction.objects.get(id=id)
    except FinancialTransaction.DoesNotExist:
        return Response({"success": False, "message": "Tranzaksiya topilmadi"}, status=404)

    if request.method == 'GET':
        return Response({"success": True, "data": TransactionResponseSerializer(tx).data})

    if request.method in ['PUT', 'PATCH']:
        serializer = TransactionCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        body_data = serializer.validated_data
        for k, v in body_data.items():
            if hasattr(tx, k) and v is not None:
                if k == 'expense_type_id':
                    v = resolve_expense_type_id(v)
                elif k == 'reference_id' and (not v or v in ['undefined', 'null']):
                    v = None
                if k == 'notes' and not v:
                    v = body_data.get('description') or ''
                setattr(tx, k, v)
        tx.save()
        record_audit_log(
            action="UPDATE", entity_name="FINANCIAL_TRANSACTION",
            entity_id=id, actor_id=request.user.id, new_values=body_data, request=request
        )
        return Response({"success": True, "data": TransactionResponseSerializer(tx).data})

    # DELETE
    tx.delete()
    record_audit_log(
        action="DELETE", entity_name="FINANCIAL_TRANSACTION",
        entity_id=id, actor_id=request.user.id, request=request
    )
    return Response({"success": True, "data": {"id": id, "deleted": True}})

