import uuid
import datetime
from decimal import Decimal
from core.exceptions import CustomAppException
from apps.purchasing.models import Purchase, PurchaseItem
from apps.warehouse.services import WarehouseService
from apps.master_data.models import Supplier, Warehouse

class PurchaseService:
    @staticmethod
    def create_purchase(data: dict, created_by_id: str) -> Purchase:
        items_data = data.pop("items", [])
        
        # 1. Purchase Number
        p_num = (data.get("purchase_number") or "").strip()
        if not p_num or p_num in ["undefined", "null"]:
            p_num = f"PUR-{datetime.date.today().year}-{str(uuid.uuid4())[:6].upper()}"

        if Purchase.objects.filter(purchase_number=p_num).exists():
            p_num = f"PUR-{datetime.date.today().year}-{str(uuid.uuid4())[:6].upper()}"

        # 2. Supplier
        sup_id = (data.get("supplier_id") or "").strip()
        supplier = None
        if sup_id and sup_id not in ["undefined", "null"]:
            supplier = Supplier.objects.filter(id=sup_id).first()
        if not supplier:
            supplier = Supplier.objects.first()
        if not supplier:
            supplier = Supplier.objects.create(code="SUP-GEN", name="Asosiy Ta'minotchi")

        # 3. Warehouse
        wh_id = (data.get("warehouse_id") or "").strip()
        warehouse = None
        if wh_id and wh_id not in ["undefined", "null"]:
            warehouse = Warehouse.objects.filter(id=wh_id).first()
        if not warehouse:
            warehouse = Warehouse.objects.first()
        if not warehouse:
            warehouse = Warehouse.objects.create(code="WH-MAIN", name="Asosiy Ombor")

        # 4. Order Date
        o_date = data.get("order_date")
        if not o_date:
            o_date = datetime.date.today()

        subtotal = Decimal("0.00")
        purchase_items_to_create = []
        for item in items_data:
            tot = Decimal(str(item.get("quantity", 1))) * Decimal(str(item.get("unit_price", 0)))
            subtotal += tot
            purchase_items_to_create.append({
                "product_id": item["product_id"],
                "quantity": Decimal(str(item.get("quantity", 1))),
                "unit_price": Decimal(str(item.get("unit_price", 0))),
                "total_price": tot
            })

        tax = Decimal(str(data.get("tax_amount", 0) or 0))
        total_amount = subtotal + tax

        purchase = Purchase.objects.create(
            purchase_number=p_num,
            supplier=supplier,
            warehouse=warehouse,
            invoice_number=data.get("invoice_number"),
            order_date=o_date,
            subtotal=subtotal,
            tax_amount=tax,
            total_amount=total_amount,
            exchange_rate_at_creation=Decimal(str(data.get("exchange_rate_at_creation", 1.0) or 1.0)),
            status="DRAFT",
            created_by_id=created_by_id
        )

        for item_dict in purchase_items_to_create:
            PurchaseItem.objects.create(purchase=purchase, **item_dict)

        return purchase

    @staticmethod
    def update_status(purchase_id: str, new_status: str, updated_by_id: str) -> Purchase:
        try:
            purchase = Purchase.objects.get(id=purchase_id)
        except Purchase.DoesNotExist:
            raise CustomAppException(message="Xarid hujjati topilmadi", status_code=404)

        if purchase.status == "RECEIVED":
            raise CustomAppException(message="Qabul qilingan xarid hujjati holatini o'zgartirib bo'lmaydi", error_code="PURCHASE_ALREADY_RECEIVED")

        if new_status == "RECEIVED":
            for item in purchase.items.all():
                WarehouseService.record_receipt(
                    warehouse_id=str(purchase.warehouse_id),
                    product_id=str(item.product_id),
                    quantity=Decimal(str(item.quantity)),
                    unit_cost=Decimal(str(item.unit_price)),
                    reference_id=str(purchase.id),
                    notes=f"Purchase receipt #{purchase.purchase_number}"
                )

        purchase.status = new_status
        purchase.updated_by_id = updated_by_id
        purchase.save()
        return purchase

    @staticmethod
    def get_multi(
        page: int = 1,
        limit: int = 20,
        status: str = None
    ):
        qs = Purchase.objects.all()

        if status:
            qs = qs.filter(status=status)

        total = qs.count()

        skip = (page - 1) * limit
        items = list(qs.order_by('-created_at')[skip:skip + limit])

        return items, total
