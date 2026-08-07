from decimal import Decimal
from django.db.models import Q
from core.exceptions import CustomAppException
from core.safe_delete import SafeDeleteService
from apps.products.models import Product, Recipe, RecipeItem, Boiler
from apps.master_data.models import WarrantyType

class ProductService:
    @staticmethod
    def get_multi(
        page: int = 1,
        limit: int = 20,
        search: str = None,
        category_id: str = None,
        product_type: str = None,
        status: str = "ACTIVE"
    ):
        qs = Product.objects.all()

        if status:
            qs = qs.filter(status=status)

        if category_id:
            qs = qs.filter(category_id=category_id)

        if product_type:
            qs = qs.filter(type=product_type)

        if search:
            qs = qs.filter(Q(name__icontains=search) | Q(code__icontains=search))

        total = qs.count()

        skip = (page - 1) * limit
        items = list(qs.order_by('-created_at')[skip:skip + limit])

        return items, total

    @staticmethod
    def create(data: dict, created_by_id: str) -> Product:
        for fk in ["category_id", "unit_id", "material_type_id", "supplier_id"]:
            if fk in data and not data[fk]:
                data[fk] = None

        if not data.get("category_id"):
            from apps.master_data.models import ProductCategory
            cat = ProductCategory.objects.first()
            if not cat:
                cat = ProductCategory.objects.create(code="CAT-DEF", name="Umumiy Kategoriya")
            data["category_id"] = cat.id

        if not data.get("unit_id"):
            from apps.master_data.models import Unit
            unit = Unit.objects.first()
            if not unit:
                unit = Unit.objects.create(code="DONA", name="dona", symbol="dona")
            data["unit_id"] = unit.id

        code = (data.get("code") or "").strip()
        if not code:
            import uuid
            code = f"SKU-{str(uuid.uuid4())[:6].upper()}"
        if Product.objects.filter(code=code).exists():
            import uuid
            code = f"SKU-{str(uuid.uuid4())[:6].upper()}"
        data["code"] = code

        if created_by_id and hasattr(Product, "created_by_id"):
            data["created_by_id"] = created_by_id

        product = Product.objects.create(**data)
        return product

    @staticmethod
    def get_by_id(product_id: str) -> Product:
        try:
            return Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            raise CustomAppException(message="Mahsulot topilmadi", status_code=404)

    @staticmethod
    def update(product_id: str, data: dict, updated_by_id: str) -> Product:
        item = ProductService.get_by_id(product_id)
        for k, v in data.items():
            if hasattr(item, k) and v is not None:
                setattr(item, k, v)
        if updated_by_id:
            item.updated_by_id = updated_by_id
        item.save()
        return item

    @staticmethod
    def delete(product_id: str) -> bool:
        item = ProductService.get_by_id(product_id)
        SafeDeleteService.check_entity_references("products", product_id)
        item.delete()
        return True


class RecipeService:
    @staticmethod
    def get_multi(page: int = 1, limit: int = 20):
        qs = Recipe.objects.all()
        total = qs.count()
        skip = (page - 1) * limit
        items = list(qs.order_by('-created_at')[skip:skip + limit])
        return items, total

    @staticmethod
    def create(data: dict, created_by_id: str = None) -> Recipe:
        items_data = data.pop("items", [])
        rec_num = (data.get("recipe_number") or "").strip()
        if not rec_num or rec_num in ["undefined", "null"]:
            import uuid
            rec_num = f"BOM-{str(uuid.uuid4())[:6].upper()}"

        if Recipe.objects.filter(recipe_number=rec_num).exists():
            import uuid
            rec_num = f"BOM-{str(uuid.uuid4())[:6].upper()}"

        data["recipe_number"] = rec_num
        if "recipe_name" in data and not data["recipe_name"]:
            data["recipe_name"] = "Nomsiz Retseptura"

        if created_by_id and hasattr(Recipe, "created_by_id"):
            data["created_by_id"] = created_by_id

        recipe = Recipe.objects.create(**data)
        for item_dict in items_data:
            RecipeItem.objects.create(recipe=recipe, **item_dict)

        return recipe

    @staticmethod
    def get_by_id(recipe_id: str) -> Recipe:
        try:
            return Recipe.objects.get(id=recipe_id)
        except Recipe.DoesNotExist:
            raise CustomAppException(message="Retsept topilmadi", status_code=404)

    @staticmethod
    def update(recipe_id: str, data: dict, updated_by_id: str = None) -> Recipe:
        recipe = RecipeService.get_by_id(recipe_id)
        items_data = data.pop("items", None)

        if "recipe_number" in data and not data["recipe_number"]:
            data.pop("recipe_number")
        if "product_id" in data and not data["product_id"]:
            data["product_id"] = None
        if "recipe_name" in data and not data["recipe_name"]:
            data["recipe_name"] = "Nomsiz Retseptura"

        for k, v in data.items():
            if hasattr(recipe, k) and v is not None:
                setattr(recipe, k, v)
        if updated_by_id and hasattr(recipe, "updated_by_id"):
            recipe.updated_by_id = updated_by_id
        recipe.save()

        if items_data is not None:
            recipe.items.all().delete()
            for item_dict in items_data:
                RecipeItem.objects.create(recipe=recipe, **item_dict)

        return recipe

    @staticmethod
    def delete(recipe_id: str) -> bool:
        recipe = RecipeService.get_by_id(recipe_id)
        recipe.delete()
        return True


class BoilerService:
    @staticmethod
    def get_multi():
        qs = Boiler.objects.all()
        if not qs.exists():
            default_boilers = [
                {"name": "Kotyol K-50kW", "model_code": "K50KW-SKU", "capacity_kw": Decimal("50.00"), "fuel_type": "GAS", "base_price": Decimal("1200.00"), "selected_stage_ids": []},
                {"name": "Kotyol K-100kW", "model_code": "K100KW-SKU", "capacity_kw": Decimal("100.00"), "fuel_type": "GAS", "base_price": Decimal("2200.00"), "selected_stage_ids": []},
            ]
            for b in default_boilers:
                Boiler.objects.create(**b)
            qs = Boiler.objects.all()
        return list(qs.order_by('-created_at'))

    @staticmethod
    def create_boiler(data: dict, created_by_id: str = None) -> Boiler:
        name = (data.get("modelName") or data.get("name") or "Yangi Kotyol").strip()
        code = (data.get("internalCode") or data.get("model_code") or data.get("code") or "").strip()
        if not code or code in ["undefined", "null"]:
            import uuid
            code = f"KTL-{str(uuid.uuid4())[:6].upper()}"

        if Boiler.objects.filter(model_code=code).exists():
            import uuid
            code = f"{code}_{str(uuid.uuid4())[:4]}"

        rec_id = (data.get("recipeId") or data.get("recipe_id") or "").strip()
        recipe = None
        if rec_id and rec_id not in ["undefined", "null"]:
            recipe = Recipe.objects.filter(id=rec_id).first()

        w_id = (data.get("warranty_type_id") or "").strip()
        warranty_type = None
        if w_id and w_id not in ["undefined", "null"]:
            warranty_type = WarrantyType.objects.filter(id=w_id).first()

        stages = data.get("selectedStageIds") or data.get("selected_stage_ids") or []

        cap = Decimal(str(data.get("capacityKw") or data.get("capacity_kw") or 50.0))
        price = Decimal(str(data.get("basePrice") or data.get("base_price") or 0.0))

        boiler = Boiler.objects.create(
            name=name,
            model_code=code,
            capacity_kw=cap,
            fuel_type=data.get("fuelType") or data.get("fuel_type") or "GAS",
            base_price=price,
            recipe=recipe,
            warranty_type=warranty_type,
            selected_stage_ids=stages,
            status=data.get("status") or "ACTIVE",
            created_by_id=created_by_id
        )
        return boiler

    @staticmethod
    def update_boiler(boiler_id: str, data: dict, updated_by_id: str = None) -> Boiler:
        try:
            boiler = Boiler.objects.get(id=boiler_id)
        except Boiler.DoesNotExist:
            raise CustomAppException(message="Kotyol modeli topilmadi", status_code=404)

        if "modelName" in data or "name" in data:
            boiler.name = (data.get("modelName") or data.get("name") or boiler.name).strip()

        if "internalCode" in data or "model_code" in data or "code" in data:
            code = (data.get("internalCode") or data.get("model_code") or data.get("code") or "").strip()
            if code:
                boiler.model_code = code

        if "recipeId" in data or "recipe_id" in data:
            rec_id = (data.get("recipeId") or data.get("recipe_id") or "").strip()
            boiler.recipe = Recipe.objects.filter(id=rec_id).first() if rec_id else None

        if "selectedStageIds" in data or "selected_stage_ids" in data:
            boiler.selected_stage_ids = data.get("selectedStageIds") or data.get("selected_stage_ids") or []

        if "status" in data and data["status"]:
            boiler.status = data["status"]

        if "capacityKw" in data or "capacity_kw" in data:
            cap = data.get("capacityKw") or data.get("capacity_kw")
            if cap is not None:
                boiler.capacity_kw = Decimal(str(cap))

        if "fuelType" in data or "fuel_type" in data:
            fuel = data.get("fuelType") or data.get("fuel_type")
            if fuel:
                boiler.fuel_type = fuel

        if "basePrice" in data or "base_price" in data:
            bp = data.get("basePrice") or data.get("base_price")
            if bp is not None:
                boiler.base_price = Decimal(str(bp))

        if updated_by_id and hasattr(boiler, "updated_by_id"):
            boiler.updated_by_id = updated_by_id

        boiler.save()
        return boiler

    @staticmethod
    def delete_boiler(boiler_id: str) -> bool:
        try:
            boiler = Boiler.objects.get(id=boiler_id)
        except Boiler.DoesNotExist:
            raise CustomAppException(message="Kotyol modeli topilmadi", status_code=404)
        boiler.delete()
        return True
