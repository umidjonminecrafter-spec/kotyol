from decimal import Decimal
from core.exceptions import CustomAppException
from apps.warehouse.models import WarehouseStock, StockMovement
from apps.master_data.models import Warehouse
from apps.products.models import Product

class WarehouseService:
    @staticmethod
    def get_stocks(
        warehouse_id: str = None,
        product_id: str = None,
        page: int = 1,
        limit: int = 20
    ):
        qs = WarehouseStock.objects.all()

        if warehouse_id:
            qs = qs.filter(warehouse_id=warehouse_id)

        if product_id:
            qs = qs.filter(product_id=product_id)

        total = qs.count()

        skip = (page - 1) * limit
        items = list(qs.order_by('-updated_at')[skip:skip + limit])

        return items, total

    @staticmethod
    def record_receipt(
        warehouse_id: str,
        product_id: str,
        quantity: Decimal,
        unit_cost: Decimal,
        reference_id: str = None,
        notes: str = None
    ) -> WarehouseStock:
        stock = WarehouseStock.objects.filter(warehouse_id=warehouse_id, product_id=product_id).first()

        if not stock:
            stock = WarehouseStock.objects.create(
                warehouse_id=warehouse_id,
                product_id=product_id,
                quantity=quantity,
                reserved_quantity=Decimal("0.000"),
                avg_unit_cost=unit_cost
            )
        else:
            old_total = stock.quantity * stock.avg_unit_cost
            new_addition = quantity * unit_cost
            new_qty = stock.quantity + quantity
            if new_qty > 0:
                stock.avg_unit_cost = (old_total + new_addition) / new_qty
            stock.quantity = new_qty
            stock.save()

        StockMovement.objects.create(
            movement_type="PURCHASE_RECEIPT",
            warehouse_id=warehouse_id,
            product_id=product_id,
            quantity=quantity,
            reference_id=reference_id,
            notes=notes
        )
        return stock

    @staticmethod
    def adjust_stock(
        warehouse_id: str,
        product_id: str,
        quantity_delta: Decimal,
        unit_cost: Decimal = Decimal("0.00"),
        movement_type: str = "ADJUSTMENT",
        notes: str = None
    ) -> WarehouseStock:
        stock = WarehouseStock.objects.filter(warehouse_id=warehouse_id, product_id=product_id).first()

        if not stock:
            stock = WarehouseStock.objects.create(
                warehouse_id=warehouse_id,
                product_id=product_id,
                quantity=max(Decimal("0.000"), quantity_delta),
                reserved_quantity=Decimal("0.000"),
                avg_unit_cost=unit_cost
            )
        else:
            stock.quantity = max(Decimal("0.000"), stock.quantity + quantity_delta)
            if unit_cost > 0:
                stock.avg_unit_cost = unit_cost
            stock.save()

        StockMovement.objects.create(
            movement_type=movement_type,
            warehouse_id=warehouse_id,
            product_id=product_id,
            quantity=quantity_delta,
            notes=notes
        )
        return stock

    @staticmethod
    def update_stock(stock_id: str, data: dict, updated_by_id: str = None) -> WarehouseStock:
        try:
            stock = WarehouseStock.objects.get(id=stock_id)
        except WarehouseStock.DoesNotExist:
            raise CustomAppException(message="Ombor qoldig'i topilmadi", status_code=404)

        if "quantity" in data and data["quantity"] is not None:
            stock.quantity = Decimal(str(data["quantity"]))
        elif "quantity_delta" in data and data["quantity_delta"] is not None and data["quantity_delta"] != 0:
            stock.quantity = max(Decimal("0.000"), stock.quantity + Decimal(str(data["quantity_delta"])))

        if "reserved_quantity" in data and data["reserved_quantity"] is not None:
            stock.reserved_quantity = Decimal(str(data["reserved_quantity"]))

        if "avg_unit_cost" in data and data["avg_unit_cost"] is not None:
            stock.avg_unit_cost = Decimal(str(data["avg_unit_cost"]))
        elif "unit_cost" in data and data["unit_cost"] is not None:
            stock.avg_unit_cost = Decimal(str(data["unit_cost"]))

        # Safely validate warehouse_id
        w_id = (str(data.get("warehouse_id") or "")).strip()
        if w_id and w_id not in ["undefined", "null"]:
            if Warehouse.objects.filter(id=w_id).exists():
                stock.warehouse_id = w_id

        # Safely validate product_id
        p_id = (str(data.get("product_id") or "")).strip()
        if p_id and p_id not in ["undefined", "null"]:
            if Product.objects.filter(id=p_id).exists():
                stock.product_id = p_id

        if updated_by_id and hasattr(stock, "updated_by_id"):
            stock.updated_by_id = updated_by_id

        stock.save()

        StockMovement.objects.create(
            movement_type=data.get("movement_type") or "UPDATE",
            warehouse_id=stock.warehouse_id,
            product_id=stock.product_id,
            quantity=stock.quantity,
            notes=data.get("notes") or "Ombor qoldig'i tahrirlandi"
        )
        return stock
