import uuid
import datetime
from decimal import Decimal
from core.exceptions import CustomAppException
from apps.sales.models import Sale
from apps.master_data.models import Customer
from apps.products.models import Boiler, Product

class SalesService:
    @staticmethod
    def create_sale(data: dict, created_by_id: str) -> Sale:
        inv_num = (data.get("invoice_number") or "").strip()
        if not inv_num or inv_num in ["undefined", "null"]:
            inv_num = f"DOC-{datetime.date.today().year}-{str(uuid.uuid4())[:6].upper()}"

        if Sale.objects.filter(invoice_number=inv_num).exists():
            inv_num = f"DOC-{datetime.date.today().year}-{str(uuid.uuid4())[:6].upper()}"

        # Resolve Customer safely
        cust_id = (data.get("customer_id") or "").strip()
        customer = None
        if cust_id and cust_id not in ["undefined", "null"]:
            customer = Customer.objects.filter(id=cust_id).first()

        if not customer:
            customer = Customer.objects.first()

        if not customer:
            customer = Customer.objects.create(code="CUST-GEN", name="Umumiy Mijoz")

        # Resolve Boiler safely
        boiler_id = (data.get("boiler_id") or "").strip()
        boiler = None
        if boiler_id and boiler_id not in ["undefined", "null"]:
            boiler = Boiler.objects.filter(id=boiler_id).first()

        # Resolve Product safely
        product_id = (data.get("product_id") or "").strip()
        product = None
        if product_id and product_id not in ["undefined", "null"]:
            product = Product.objects.filter(id=product_id).first()

        qty = Decimal(str(data.get("quantity", 1.0) or 1.0))
        unit_price = Decimal(str(data.get("unit_price", 0.0) or 0.0))
        subtotal = qty * unit_price
        disc = Decimal(str(data.get("discount_amount", 0) or 0))
        tax = Decimal(str(data.get("tax_amount", 0) or 0))
        total_amount = subtotal - disc + tax

        sale = Sale.objects.create(
            invoice_number=inv_num,
            customer=customer,
            boiler=boiler,
            product=product,
            quantity=qty,
            unit_price=unit_price,
            subtotal=subtotal,
            discount_amount=disc,
            tax_amount=tax,
            total_amount=total_amount,
            exchange_rate_at_creation=Decimal(str(data.get("exchange_rate_at_creation", 1.0) or 1.0)),
            payment_status=data.get("payment_status") or "UNPAID",
            delivery_status=data.get("delivery_status") or "PENDING",
            created_by_id=created_by_id,
            assigned_employee_id=data.get("assigned_employee_id"),
            assigned_employee_name=data.get("assigned_employee_name"),
            warranty_period=data.get("warranty_period"),
            warranty_start_date=data.get("warranty_start_date") or None,
            warranty_end_date=data.get("warranty_end_date") or None,
            delivery_location=data.get("delivery_location"),
            notes=data.get("notes")
        )
        return sale

    @staticmethod
    def update_status(sale_id: str, data: dict, updated_by_id: str) -> Sale:
        try:
            sale = Sale.objects.get(id=sale_id)
        except Sale.DoesNotExist:
            raise CustomAppException(message="Sotuv hujjati topilmadi", status_code=404)

        if "payment_status" in data and data["payment_status"]:
            sale.payment_status = data["payment_status"]
        if "delivery_status" in data and data["delivery_status"]:
            sale.delivery_status = data["delivery_status"]

        sale.updated_by_id = updated_by_id
        sale.save()
        return sale

    @staticmethod
    def update_sale(sale_id: str, data: dict, updated_by_id: str) -> Sale:
        try:
            sale = Sale.objects.get(id=sale_id)
        except Sale.DoesNotExist:
            raise CustomAppException(message="Sotuv hujjati topilmadi", status_code=404)

        # Update fields that are provided
        for field in ['quantity', 'unit_price', 'discount_amount', 'tax_amount', 'exchange_rate_at_creation']:
            val = data.get(field)
            if val is not None:
                setattr(sale, field, Decimal(str(val)))

        if data.get('customer_id'):
            cust = Customer.objects.filter(id=data['customer_id']).first()
            if cust:
                sale.customer = cust

        if data.get('boiler_id'):
            boiler = Boiler.objects.filter(id=data['boiler_id']).first()
            if boiler:
                sale.boiler = boiler

        if data.get('product_id'):
            product = Product.objects.filter(id=data['product_id']).first()
            if product:
                sale.product = product

        # Recalculate totals
        sale.subtotal = sale.quantity * sale.unit_price
        sale.total_amount = sale.subtotal - sale.discount_amount + sale.tax_amount

        # Update additional fields
        for field in ['assigned_employee_id', 'assigned_employee_name', 'warranty_period', 'warranty_start_date', 'warranty_end_date', 'delivery_location', 'notes', 'payment_status', 'delivery_status']:
            if field in data and data[field] is not None:
                val = data[field]
                if val == "":
                    val = None
                setattr(sale, field, val)

        if 'status' in data and data['status'] is not None:
            sale.status = str(data['status'])

        sale.updated_by_id = updated_by_id
        sale.save()
        return sale

    @staticmethod
    def generate_receipt_data(sale_id: str) -> dict:
        try:
            sale = Sale.objects.get(id=sale_id)
        except Sale.DoesNotExist:
            raise CustomAppException(message="Sotuv hujjati topilmadi", status_code=404)

        from apps.master_data.models import Company
        company = Company.objects.first()

        item_name = "Noma'lum mahsulot"
        if sale.boiler:
            item_name = sale.boiler.name
        elif sale.product:
            item_name = sale.product.name

        return {
            "receipt_title": "SOTUV CHEKI / SCHYOT-FAKTURA",
            "company": {
                "name": company.name if company else "Kotyol ERP Enterprise",
                "phone": company.phone if company else "",
                "address": company.address if company else "",
                "website": company.website if company else "",
                "currency": company.currency if company else "UZS",
            },
            "sale_info": {
                "id": sale.id,
                "invoice_number": sale.invoice_number,
                "date": sale.created_at.strftime("%Y-%m-%d %H:%M:%S") if sale.created_at else "",
                "payment_status": sale.payment_status,
                "delivery_status": sale.delivery_status,
                "assigned_employee": sale.assigned_employee_name or "",
            },
            "customer": {
                "name": sale.customer.name if sale.customer else "Noma'lum mijoz",
                "phone": sale.customer.phone if sale.customer else "",
                "address": sale.customer.address if sale.customer else "",
            },
            "item": {
                "name": item_name,
                "quantity": float(sale.quantity),
                "unit_price": float(sale.unit_price),
                "subtotal": float(sale.subtotal),
            },
            "financials": {
                "subtotal": float(sale.subtotal),
                "discount_amount": float(sale.discount_amount),
                "tax_amount": float(sale.tax_amount),
                "total_amount": float(sale.total_amount),
                "exchange_rate": float(sale.exchange_rate_at_creation),
            },
            "warranty": {
                "period": sale.warranty_period or "",
                "start_date": str(sale.warranty_start_date) if sale.warranty_start_date else "",
                "end_date": str(sale.warranty_end_date) if sale.warranty_end_date else "",
            },
            "notes": sale.notes or "",
        }

    @staticmethod
    def get_multi(
        page: int = 1,
        limit: int = 20
    ):
        qs = Sale.objects.all()
        total = qs.count()

        skip = (page - 1) * limit
        items = list(qs.order_by('-created_at')[skip:skip + limit])

        return items, total

