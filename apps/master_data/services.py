from core.exceptions import CustomAppException
from core.safe_delete import SafeDeleteService
from apps.master_data.models import (
    ProductCategory, SupplierCategory, MaterialType, Unit, Supplier, Customer,
    Warehouse, WarrantyType, CustomerType, ServiceType, Priority, OrderStatus, ExpenseType, SalaryType, ProductionStage, InsuranceType,
    Currency, DefectReason, Role, PermissionsMatrix, ServiceTicket
)

MASTER_DATA_MODELS = {
    "product-categories": ProductCategory,
    "product-category": ProductCategory,
    "supplier-categories": SupplierCategory,
    "supplier-category": SupplierCategory,
    "production-stages": ProductionStage,
    "production-stage": ProductionStage,
    "insurance-types": InsuranceType,
    "insurance-type": InsuranceType,
    "material-types": MaterialType,
    "material-type": MaterialType,
    "units": Unit,
    "unit": Unit,
    "suppliers": Supplier,
    "supplier": Supplier,
    "customers": Customer,
    "customer": Customer,
    "warehouses": Warehouse,
    "warehouse": Warehouse,
    "warranty-types": WarrantyType,
    "warranty-type": WarrantyType,
    "warranties": WarrantyType,
    "warranty": WarrantyType,
    "customer-types": CustomerType,
    "customer-type": CustomerType,
    "service-types": ServiceType,
    "service-type": ServiceType,
    "services": ServiceTicket,
    "service": ServiceTicket,
    "service-tickets": ServiceTicket,
    "service_tickets": ServiceTicket,
    "priorities": Priority,
    "priority": Priority,
    "order-statuses": OrderStatus,
    "order-status": OrderStatus,
    "statuses": OrderStatus,
    "status": OrderStatus,
    "expense-types": ExpenseType,
    "expense-type": ExpenseType,
    "expenses": ExpenseType,
    "expense": ExpenseType,
    "salary-types": SalaryType,
    "salary-type": SalaryType,
    "salaries": SalaryType,
    "salary": SalaryType,
    "currencies": Currency,
    "currency": Currency,
    "defect-reasons": DefectReason,
    "defect_reasons": DefectReason,
    "defect-reason": DefectReason,
    "roles": Role,
    "role": Role,
    "permissions-matrix": PermissionsMatrix,
    "permissions_matrix": PermissionsMatrix,
    "permissions": PermissionsMatrix,
    "permission": PermissionsMatrix,
}

class MasterDataService:
    @staticmethod
    def get_model(entity_key: str):
        normalized_key = str(entity_key).lower().strip().replace('_', '-')
        model = MASTER_DATA_MODELS.get(normalized_key)
        if not model:
            raise CustomAppException(message=f"Entity key '{entity_key}' topilmadi", status_code=404)
        return model

    @classmethod
    def get_multi(cls, entity_key: str, include_archived: bool = False):
        model = cls.get_model(entity_key)
        
        # Auto seed Priority if empty
        if model == Priority and not model.objects.exists():
            default_priorities = [
                {"code": "LOW", "name": "Past"},
                {"code": "NORMAL", "name": "Oddiy"},
                {"code": "HIGH", "name": "Yuqori"},
                {"code": "URGENT", "name": "Shoshilinch"},
            ]
            for p in default_priorities:
                model.objects.create(**p)

        # Auto seed OrderStatus if empty
        if model == OrderStatus and not model.objects.exists():
            default_statuses = [
                {"code": "NEW", "name": "Yangi"},
                {"code": "RESERVED", "name": "Rezervda"},
                {"code": "IN_PRODUCTION", "name": "Ishlab Chiqarishda"},
                {"code": "COMPLETED", "name": "Tayyor"},
                {"code": "CANCELLED", "name": "Bekor Qilingan"},
            ]
            for st in default_statuses:
                model.objects.create(**st)

        # Auto seed CustomerType if empty
        if model == CustomerType and not model.objects.exists():
            default_ctypes = [
                {"code": "INDIVIDUAL", "name": "Jismoniy Shaxs"},
                {"code": "CORPORATE", "name": "Yuridik Shaxs"},
                {"code": "WHOLESALE", "name": "Ulgurji Xaridor"},
            ]
            for ct in default_ctypes:
                model.objects.create(**ct)

        # Auto seed Warehouse if empty
        if model == Warehouse and not model.objects.exists():
            default_whs = [
                {"code": "WH-MAIN", "name": "Asosiy Ombor", "location": "Toshkent"},
            ]
            for wh in default_whs:
                model.objects.create(**wh)

        # Auto seed SupplierCategory if empty
        if model == SupplierCategory and not model.objects.exists():
            default_scats = [
                {"code": "RAW-MATERIALS", "name": "Xom ashyo", "description": "Xom ashyo materiallari"},
                {"code": "COMPONENTS", "name": "Ehtiyot qismlar", "description": "Ehtiyot qismlar va butlovchilar"},
                {"code": "EQUIPMENT", "name": "Uskunalar", "description": "Dastgohlar va uskunalar"},
                {"code": "SERVICES", "name": "Xizmatlar", "description": "Tashqi xizmatlar"},
                {"code": "LOGISTICS", "name": "Logistika", "description": "Transport va logistika"},
            ]
            for sc in default_scats:
                model.objects.create(**sc)

        # Auto seed ProductionStage if empty
        if model == ProductionStage and not model.objects.exists():
            default_stages = [
                {"code": "PLANNED", "name": "Rejalashtirilgan", "sequence": 10},
                {"code": "CUTTING", "name": "Bichish / Kesish", "sequence": 20},
                {"code": "WELDING", "name": "Payvandlash", "sequence": 30},
                {"code": "ASSEMBLY", "name": "Yig'ish", "sequence": 40},
                {"code": "TESTING", "name": "Sinov va Nazorat", "sequence": 50},
                {"code": "COMPLETED", "name": "Bajarildi", "sequence": 60},
            ]
            for stg in default_stages:
                model.objects.create(**stg)

        # Auto seed InsuranceType if empty
        if model == InsuranceType and not model.objects.exists():
            default_ins = [
                {"code": "ACCIDENT", "name": "Baxtsiz hodisalardan sug'urta", "description": "Xodimlar uchun majburiy sug'urta"},
                {"code": "HEALTH", "name": "Tibbiy sug'urta", "description": "Ixtiyoriy tibbiy sug'urta paketi"},
                {"code": "PROPERTY", "name": "Mulk sug'urtasi", "description": "Ombor va uskunalar sug'urtasi"},
                {"code": "LIABILITY", "name": "Fuqarolik javobgarligi sug'urtasi", "description": "Uchinchi shaxslar oldidagi javobgarlik"},
            ]
            for ins in default_ins:
                model.objects.create(**ins)

        # Auto seed ServiceType if empty
        if model == ServiceType and not model.objects.exists():
            default_services = [
                {"code": "INSTALLATION", "name": "O'rnatish va Montaj"},
                {"code": "MAINTENANCE", "name": "Texnik Xizmat Ko'rsatish"},
                {"code": "REPAIR", "name": "Ta'mirlash Hizmati"},
                {"code": "DIAGNOSTICS", "name": "Diagnostika va Tekshiruv"},
            ]
            for srv in default_services:
                model.objects.create(**srv)

        # Auto seed Currency if empty
        if model == Currency and not model.objects.exists():
            default_currencies = [
                {"code": "USD", "name": "AQSH Dollari", "symbol": "$", "exchange_rate": 1.0000},
                {"code": "UZS", "name": "O'zbekiston So'mi", "symbol": "so'm", "exchange_rate": 12800.0000},
                {"code": "EUR", "name": "Yevro", "symbol": "€", "exchange_rate": 1.0800},
            ]
            for c in default_currencies:
                model.objects.create(**c)

        # Auto seed DefectReason if empty
        if model == DefectReason and not model.objects.exists():
            default_defects = [
                {"code": "MATERIAL_DEFECT", "name": "Xom-ashyo nuqsoni", "description": "Xom-ashyo sifatiga mos emasligi"},
                {"code": "WELDING_DEFECT", "name": "Payvandlash xatosi", "description": "Payvand chokining noto'liq yoki darz ketganligi"},
                {"code": "ASSEMBLY_DEFECT", "name": "Yig'ish nuqsoni", "description": "Yig'ish jarayonidagi xatolik"},
            ]
            for d in default_defects:
                model.objects.create(**d)

        # Auto seed Role if empty
        if model == Role and not model.objects.exists():
            default_roles = [
                {"code": "ADMIN", "name": "Tizim Administratori", "description": "To'liq ruxsatlar"},
                {"code": "MANAGER", "name": "Menejer", "description": "Boshqaruv va hisobotlar"},
                {"code": "TECHNICIAN", "name": "Texnik / Usta", "description": "Ishlab chiqarish va servis"},
                {"code": "WAREHOUSEMAN", "name": "Omborchi", "description": "Ombor va zaxiralar"},
            ]
            for r in default_roles:
                model.objects.create(**r)

        # Auto seed PermissionsMatrix if empty
        if model == PermissionsMatrix and not model.objects.exists():
            default_perms = [
                {"code": "READ_PRODUCTS", "name": "Mahsulotlarni ko'rish", "module": "PRODUCTS"},
                {"code": "WRITE_PRODUCTS", "name": "Mahsulotlarni tahrirlash", "module": "PRODUCTS"},
                {"code": "READ_ORDERS", "name": "Buyurtmalarni ko'rish", "module": "ORDERS"},
                {"code": "WRITE_ORDERS", "name": "Buyurtmalarni yaratish/tahrirlash", "module": "ORDERS"},
            ]
            for p in default_perms:
                model.objects.create(**p)

        qs = model.objects.all()
        if not include_archived:
            qs = qs.exclude(status="ARCHIVED")

        if hasattr(model, 'sequence'):
            items = list(qs.order_by("sequence", "-created_at")[:1000])
        else:
            items = list(qs.order_by("-created_at")[:1000])

        total = qs.count()
        return items, total

    @classmethod
    def create(cls, entity_key: str, data: dict, created_by_id: str):
        model = cls.get_model(entity_key)

        # 1. Resolve name
        name_val = (data.get("name") or data.get("company_name") or data.get("title") or data.get("supplier_name") or "").strip()
        if not name_val:
            name_val = "Yangi Yozuv"
        data["name"] = name_val

        model_fields = {f.name for f in model._meta.get_fields()}

        # Normalize fields based on available model fields
        if "months" in model_fields:
            m_val = data.get("months") or data.get("duration") or data.get("duration_months")
            if m_val is not None:
                data["months"] = int(float(m_val))

        if "symbol" in model_fields:
            s_val = data.get("symbol") or data.get("short_name") or data.get("shortName")
            if s_val is not None:
                data["symbol"] = str(s_val)

        if "exchange_rate" in model_fields:
            e_val = data.get("exchange_rate") or data.get("rate_to_usd") or data.get("rateToUSD")
            if e_val is not None:
                data["exchange_rate"] = float(e_val)

        if "phone" in model_fields:
            p_val = data.get("phone") or data.get("mobile") or data.get("altPhone")
            if not p_val and "address" in data and isinstance(data["address"], str) and "{" in data["address"]:
                try:
                    import json
                    parsed_addr = json.loads(data["address"])
                    if isinstance(parsed_addr, dict):
                        p_val = parsed_addr.get("phone") or parsed_addr.get("altPhone") or parsed_addr.get("mobile")
                except Exception:
                    pass
            if p_val:
                data["phone"] = str(p_val).strip()

        # 2. Resolve code
        code_val = data.get("code") or data.get("symbol") or data.get("short_name") or data.get("shortName")
        if code_val and str(code_val).strip() and str(code_val).strip() not in ["undefined", "null", ""]:
            code_val = str(code_val).strip()
            if model.objects.filter(code=code_val).exists():
                import uuid
                code_val = f"{code_val}_{str(uuid.uuid4())[:4]}"
            data["code"] = code_val
        else:
            import uuid
            name_prefix = name_val.upper().replace(" ", "_")[:15]
            data["code"] = f"{name_prefix}_{str(uuid.uuid4())[:6]}"
        
        valid_data = {k: v for k, v in data.items() if k in model_fields and v is not None}

        if created_by_id and "created_by_id" in model_fields:
            valid_data["created_by_id"] = created_by_id

        item = model.objects.create(**valid_data)
        return item


    @classmethod
    def update(cls, entity_key: str, item_id: str, data: dict, updated_by_id: str):
        model = cls.get_model(entity_key)
        try:
            item = model.objects.get(id=item_id)
        except model.DoesNotExist:
            raise CustomAppException(message="Master data ob'ekti topilmadi", status_code=404)
        
        name_val = (data.get("name") or data.get("company_name") or data.get("title") or data.get("supplier_name") or "").strip()
        if name_val:
            data["name"] = name_val

        model_fields = {f.name for f in model._meta.get_fields()}

        # Normalize fields based on available model fields
        if "months" in model_fields:
            m_val = data.get("months") or data.get("duration") or data.get("duration_months")
            if m_val is not None:
                data["months"] = int(float(m_val))

        if "symbol" in model_fields:
            s_val = data.get("symbol") or data.get("short_name") or data.get("shortName")
            if s_val is not None:
                data["symbol"] = str(s_val)

        if "exchange_rate" in model_fields:
            e_val = data.get("exchange_rate") or data.get("rate_to_usd") or data.get("rateToUSD")
            if e_val is not None:
                data["exchange_rate"] = float(e_val)

        if "phone" in model_fields:
            p_val = data.get("phone") or data.get("mobile") or data.get("altPhone")
            if not p_val and "address" in data and isinstance(data["address"], str) and "{" in data["address"]:
                try:
                    import json
                    parsed_addr = json.loads(data["address"])
                    if isinstance(parsed_addr, dict):
                        p_val = parsed_addr.get("phone") or parsed_addr.get("altPhone") or parsed_addr.get("mobile")
                except Exception:
                    pass
            if p_val:
                data["phone"] = str(p_val).strip()

        for k, v in data.items():
            if k in model_fields and v is not None and hasattr(item, k):
                setattr(item, k, v)
        if updated_by_id and "updated_by_id" in model_fields:
            item.updated_by_id = updated_by_id
        item.save()
        return item


    @classmethod
    def archive(cls, entity_key: str, item_id: str, updated_by_id: str):
        model = cls.get_model(entity_key)
        try:
            item = model.objects.get(id=item_id)
        except model.DoesNotExist:
            raise CustomAppException(message="Master data ob'ekti topilmadi", status_code=404)
        item.status = "ARCHIVED"
        item.is_active = False
        if updated_by_id and hasattr(item, "updated_by_id"):
            item.updated_by_id = updated_by_id
        item.save()
        return item

    @classmethod
    def restore(cls, entity_key: str, item_id: str, updated_by_id: str):
        model = cls.get_model(entity_key)
        try:
            item = model.objects.get(id=item_id)
        except model.DoesNotExist:
            raise CustomAppException(message="Master data ob'ekti topilmadi", status_code=404)
        item.status = "ACTIVE"
        item.is_active = True
        if updated_by_id and hasattr(item, "updated_by_id"):
            item.updated_by_id = updated_by_id
        item.save()
        return item

    @classmethod
    def delete(cls, entity_key: str, item_id: str):
        model = cls.get_model(entity_key)
        try:
            item = model.objects.get(id=item_id)
        except model.DoesNotExist:
            raise CustomAppException(message="Master data ob'ekti topilmadi", status_code=404)

        SafeDeleteService.check_entity_references(entity_key, item_id)
        item.delete()
        return True
