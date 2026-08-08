from decimal import Decimal
from django.db.models import Q
from core.exceptions import CustomAppException
from apps.sales.models import Order
from apps.master_data.models import Customer
from apps.products.models import Boiler
from apps.production.models import ProductionBatch

class OrderService:
    @staticmethod
    def get_multi(
        page: int = 1,
        limit: int = 20,
        search: str = None,
        status: str = None,
        priority: str = None,
        customer_id: str = None
    ):
        qs = Order.objects.all()

        if status:
            qs = qs.filter(status=status)
        if priority:
            qs = qs.filter(priority=priority)
        if customer_id:
            qs = qs.filter(customer_id=customer_id)
        if search:
            qs = qs.filter(
                Q(order_number__icontains=search) |
                Q(order_name__icontains=search) |
                Q(customer_name__icontains=search) |
                Q(boiler_model_name__icontains=search)
            )

        total = qs.count()

        # Seed sample orders if completely empty
        if total == 0:
            sample_orders = [
                {
                    "order_number": "ORD-2026-1001",
                    "order_name": "Asosiy Zavod Buyurtmasi",
                    "customer_name": "Navoiy Azot AJ",
                    "boiler_model_name": "Kotyol K-50kW",
                    "quantity": Decimal("2.000"),
                    "unit_price": Decimal("1500.00"),
                    "total_amount": Decimal("3000.00"),
                    "deposit_amount": Decimal("1000.00"),
                    "auto_discount_on_late": True,
                    "late_discount_rate": Decimal("0.50"),
                    "priority": "HIGH",
                    "status": "NEW",
                },
                {
                    "order_number": "ORD-2026-1002",
                    "order_name": "Issiqlik Tizimi Qozoni",
                    "customer_name": "Toshkent Issiqlik Manbai",
                    "boiler_model_name": "Kotyol K-100kW",
                    "quantity": Decimal("1.000"),
                    "unit_price": Decimal("2500.00"),
                    "total_amount": Decimal("2500.00"),
                    "deposit_amount": Decimal("500.00"),
                    "auto_discount_on_late": True,
                    "late_discount_rate": Decimal("0.50"),
                    "priority": "NORMAL",
                    "status": "IN_PRODUCTION",
                }
            ]
            for s in sample_orders:
                Order.objects.create(**s)
            qs = Order.objects.all()
            total = qs.count()

        skip = (page - 1) * limit
        items = list(qs.order_by('-created_at')[skip:skip + limit])
        return items, total

    @staticmethod
    def create_order(data: dict, created_by_id: str = None) -> Order:
        num = (data.get("order_number") or "").strip()
        if not num or num in ["undefined", "null"]:
            import uuid
            num = f"ORD-2026-{str(uuid.uuid4())[:6].upper()}"

        if Order.objects.filter(order_number=num).exists():
            import uuid
            num = f"{num}_{str(uuid.uuid4())[:4]}"

        cust_id = (data.get("customer_id") or data.get("customerId") or "").strip()
        customer = None
        if cust_id and cust_id not in ["undefined", "null"]:
            customer = Customer.objects.filter(id=cust_id).first()

        b_id = (data.get("boiler_id") or data.get("boilerId") or "").strip()
        boiler = None
        if b_id and b_id not in ["undefined", "null"]:
            boiler = Boiler.objects.filter(id=b_id).first()

        qty = Decimal(str(data.get("quantity") or 1.0))
        price = Decimal(str(data.get("unit_price") or data.get("unitPrice") or 0.0))
        tot = Decimal(str(data.get("total_amount") or data.get("totalAmount") or (qty * price)))
        dep = Decimal(str(data.get("deposit_amount") or data.get("depositAmount") or 0.0))

        d_date = data.get("expected_delivery_date") or data.get("expectedDeliveryDate") or data.get("delivery_date") or data.get("deliveryDate")
        if not d_date or str(d_date).strip() in ["undefined", "null"]:
            d_date = None

        auto_disc = data.get("auto_discount_on_late")
        if auto_disc is None:
            auto_disc = data.get("autoDiscountOnLate", True)
        auto_disc = bool(auto_disc)

        late_rate = Decimal(str(data.get("late_discount_rate") or data.get("lateDiscountRate") or 0.5))

        emp_id = (data.get("assigned_employee_id") or data.get("assignedEmployeeId") or "").strip()
        emp_name = (data.get("assigned_employee_name") or data.get("assignedEmployeeName") or "").strip()

        order = Order.objects.create(
            order_number=num,
            order_name=(data.get("order_name") or data.get("orderName") or "Yangi buyurtma").strip(),
            customer=customer,
            customer_name=(data.get("customer_name") or data.get("customerName") or (customer.name if customer else "")).strip(),
            boiler=boiler,
            boiler_model_name=(data.get("boiler_model_name") or data.get("boilerModelName") or (boiler.name if boiler else "")).strip(),
            quantity=qty,
            unit_price=price,
            total_amount=tot,
            deposit_amount=dep,
            auto_discount_on_late=auto_disc,
            late_discount_rate=late_rate,
            assigned_employee_id=emp_id,
            assigned_employee_name=emp_name,
            priority=data.get("priority") or "HIGH",
            status=data.get("status") or "NEW",
            delivery_date=d_date,
            notes=(data.get("notes") or "").strip(),
            created_by_id=created_by_id
        )
        return order

    @staticmethod
    def get_by_id(order_id: str) -> Order:
        try:
            return Order.objects.get(id=order_id)
        except Order.DoesNotExist:
            raise CustomAppException(message="Buyurtma topilmadi", status_code=404)

    @staticmethod
    def update_order(order_id: str, data: dict, updated_by_id: str = None) -> Order:
        order = OrderService.get_by_id(order_id)

        if "order_name" in data or "orderName" in data:
            order.order_name = (data.get("order_name") or data.get("orderName") or "").strip()
        if "customer_name" in data or "customerName" in data:
            order.customer_name = (data.get("customer_name") or data.get("customerName") or "").strip()
        if "boiler_model_name" in data or "boilerModelName" in data:
            order.boiler_model_name = (data.get("boiler_model_name") or data.get("boilerModelName") or "").strip()
        if "assigned_employee_id" in data or "assignedEmployeeId" in data:
            order.assigned_employee_id = (data.get("assigned_employee_id") or data.get("assignedEmployeeId") or "").strip()
        if "assigned_employee_name" in data or "assignedEmployeeName" in data:
            order.assigned_employee_name = (data.get("assigned_employee_name") or data.get("assignedEmployeeName") or "").strip()

        if "quantity" in data and data["quantity"] is not None:
            order.quantity = Decimal(str(data["quantity"]))
        if "unit_price" in data or "unitPrice" in data:
            up = data.get("unit_price") or data.get("unitPrice")
            if up is not None:
                order.unit_price = Decimal(str(up))
        if "total_amount" in data or "totalAmount" in data:
            ta = data.get("total_amount") or data.get("totalAmount")
            if ta is not None:
                order.total_amount = Decimal(str(ta))
        if "deposit_amount" in data or "depositAmount" in data:
            dep = data.get("deposit_amount") or data.get("depositAmount")
            if dep is not None:
                order.deposit_amount = Decimal(str(dep))

        if "auto_discount_on_late" in data or "autoDiscountOnLate" in data:
            ad = data.get("auto_discount_on_late") if "auto_discount_on_late" in data else data.get("autoDiscountOnLate")
            if ad is not None:
                order.auto_discount_on_late = bool(ad)

        if "late_discount_rate" in data or "lateDiscountRate" in data:
            lr = data.get("late_discount_rate") or data.get("lateDiscountRate")
            if lr is not None:
                order.late_discount_rate = Decimal(str(lr))

        if "delivery_date" in data or "deliveryDate" in data or "expected_delivery_date" in data or "expectedDeliveryDate" in data:
            dd = data.get("expected_delivery_date") or data.get("expectedDeliveryDate") or data.get("delivery_date") or data.get("deliveryDate")
            order.delivery_date = dd if dd and str(dd).strip() not in ["undefined", "null"] else None

        if "priority" in data and data["priority"]:
            order.priority = data["priority"]
        if "status" in data and data["status"]:
            order.status = data["status"]
        if "notes" in data:
            order.notes = data["notes"]

        if updated_by_id and hasattr(order, "updated_by_id"):
            order.updated_by_id = updated_by_id

        order.save()
        return order

    @staticmethod
    def delete_order(order_id: str) -> bool:
        order = OrderService.get_by_id(order_id)
        order.delete()
        return True

    @staticmethod
    def start_production(order_id: str, updated_by_id: str = None) -> dict:
        order = OrderService.get_by_id(order_id)
        order.status = "IN_PRODUCTION"
        if updated_by_id and hasattr(order, "updated_by_id"):
            order.updated_by_id = updated_by_id
        order.save()

        # Create production batch if boiler exists
        boiler_id = order.boiler.id if order.boiler else None
        if not boiler_id:
            first_b = Boiler.objects.first()
            boiler_id = first_b.id if first_b else None

        import uuid
        batch_number = f"BATCH-{str(uuid.uuid4())[:6].upper()}"

        batch = None
        if boiler_id:
            batch = ProductionBatch.objects.create(
                batch_number=batch_number,
                boiler_id=boiler_id,
                target_quantity=int(round(float(order.quantity or 1))),
                completed_quantity=0,
                defect_quantity=0,
                status="PLANNED",
                created_by_id=updated_by_id
            )

        return {
            "order": order,
            "batch_id": batch.id if batch else None,
            "batch_number": batch.batch_number if batch else batch_number
        }
