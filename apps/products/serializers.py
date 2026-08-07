from rest_framework import serializers

class ProductCreateSerializer(serializers.Serializer):
    code = serializers.CharField(required=False, allow_null=True, allow_blank=True, default="")
    name = serializers.CharField()
    category_id = serializers.CharField(required=False, allow_null=True, allow_blank=True, default="")
    material_type_id = serializers.CharField(required=False, allow_null=True, allow_blank=True, default="")
    unit_id = serializers.CharField(required=False, allow_null=True, allow_blank=True, default="")
    supplier_id = serializers.CharField(required=False, allow_null=True, allow_blank=True, default="")
    type = serializers.CharField(required=False, allow_null=True, allow_blank=True, default="FINISHED_GOOD")
    min_stock_level = serializers.FloatField(required=False, allow_null=True, default=0.0)
    unit_price = serializers.FloatField(required=False, allow_null=True, default=0.0)
    currency = serializers.CharField(required=False, allow_null=True, allow_blank=True, default="USD")

class ProductUpdateSerializer(serializers.Serializer):
    name = serializers.CharField(required=False, allow_null=True)
    category_id = serializers.CharField(required=False, allow_null=True)
    material_type_id = serializers.CharField(required=False, allow_null=True)
    unit_id = serializers.CharField(required=False, allow_null=True)
    supplier_id = serializers.CharField(required=False, allow_null=True)
    type = serializers.CharField(required=False, allow_null=True)
    min_stock_level = serializers.FloatField(required=False, allow_null=True)
    unit_price = serializers.FloatField(required=False, allow_null=True)
    currency = serializers.CharField(required=False, allow_null=True)
    status = serializers.CharField(required=False, allow_null=True)

class ProductResponseSerializer(serializers.Serializer):
    id = serializers.CharField()
    code = serializers.CharField()
    name = serializers.CharField()
    category_id = serializers.CharField()
    category_name = serializers.SerializerMethodField()
    material_type_id = serializers.CharField(allow_null=True, required=False)
    material_type_name = serializers.SerializerMethodField()
    unit_id = serializers.CharField()
    unit_name = serializers.SerializerMethodField()
    supplier_id = serializers.CharField(allow_null=True, required=False)
    supplier_name = serializers.SerializerMethodField()
    type = serializers.CharField()
    unit_price = serializers.FloatField()
    min_stock_level = serializers.FloatField()
    currency = serializers.CharField()
    status = serializers.CharField()
    created_at = serializers.DateTimeField()

    def get_category_name(self, obj):
        return obj.category.name if getattr(obj, 'category', None) else None

    def get_material_type_name(self, obj):
        return obj.material_type.name if getattr(obj, 'material_type', None) else None

    def get_unit_name(self, obj):
        return obj.unit.name if getattr(obj, 'unit', None) else None

    def get_supplier_name(self, obj):
        return obj.supplier.name if getattr(obj, 'supplier', None) else None

class RecipeItemSchemaSerializer(serializers.Serializer):
    material_product_id = serializers.CharField()
    quantity = serializers.FloatField()
    waste_percentage = serializers.FloatField(default=0.0)

class RecipeItemResponseSerializer(serializers.Serializer):
    id = serializers.CharField()
    recipe_id = serializers.CharField()
    material_product_id = serializers.CharField()
    material_name = serializers.SerializerMethodField()
    quantity = serializers.FloatField()
    waste_percentage = serializers.FloatField()
    unit_price = serializers.SerializerMethodField()

    def get_material_name(self, obj):
        return obj.material_product.name if getattr(obj, 'material_product', None) else None

    def get_unit_price(self, obj):
        return float(obj.material_product.unit_price or 0.0) if getattr(obj, 'material_product', None) else 0.0

class RecipeCreateSerializer(serializers.Serializer):
    recipe_number = serializers.CharField(required=False, allow_null=True, allow_blank=True, default="")
    recipe_name = serializers.CharField(required=False, allow_null=True, allow_blank=True, default="Nomsiz Retseptura")
    product_id = serializers.CharField(required=False, allow_null=True, allow_blank=True, default=None)
    version = serializers.CharField(default="v1.0")
    estimated_cost = serializers.FloatField(default=0.0)
    items = RecipeItemSchemaSerializer(many=True, required=False, default=[])

class RecipeResponseSerializer(serializers.Serializer):
    id = serializers.CharField()
    recipe_number = serializers.CharField()
    recipe_name = serializers.CharField()
    product_id = serializers.CharField(allow_null=True, required=False)
    version = serializers.CharField()
    estimated_cost = serializers.FloatField()
    status = serializers.CharField()
    items = RecipeItemResponseSerializer(many=True, required=False, default=[])

class BoilerCreateSerializer(serializers.Serializer):
    modelName = serializers.CharField(required=False, allow_null=True, allow_blank=True, default="")
    name = serializers.CharField(required=False, allow_null=True, allow_blank=True, default="")
    internalCode = serializers.CharField(required=False, allow_null=True, allow_blank=True, default="")
    model_code = serializers.CharField(required=False, allow_null=True, allow_blank=True, default="")
    code = serializers.CharField(required=False, allow_null=True, allow_blank=True, default="")
    recipeId = serializers.CharField(required=False, allow_null=True, allow_blank=True, default="")
    recipe_id = serializers.CharField(required=False, allow_null=True, allow_blank=True, default="")
    selectedStageIds = serializers.ListField(child=serializers.CharField(), required=False, default=list)
    selected_stage_ids = serializers.ListField(child=serializers.CharField(), required=False, default=list)
    capacityKw = serializers.FloatField(required=False, allow_null=True, default=50.0)
    capacity_kw = serializers.FloatField(required=False, allow_null=True, default=50.0)
    fuelType = serializers.CharField(required=False, allow_null=True, allow_blank=True, default="GAS")
    fuel_type = serializers.CharField(required=False, allow_null=True, allow_blank=True, default="GAS")
    basePrice = serializers.FloatField(required=False, allow_null=True, default=0.0)
    base_price = serializers.FloatField(required=False, allow_null=True, default=0.0)
    warranty_type_id = serializers.CharField(required=False, allow_null=True, allow_blank=True, default="")
    status = serializers.CharField(required=False, allow_null=True, allow_blank=True, default="ACTIVE")

class BoilerResponseSerializer(serializers.Serializer):
    id = serializers.CharField()
    modelName = serializers.SerializerMethodField()
    name = serializers.CharField()
    internalCode = serializers.SerializerMethodField()
    model_code = serializers.CharField()
    code = serializers.SerializerMethodField()
    recipeId = serializers.SerializerMethodField()
    recipe_id = serializers.SerializerMethodField()
    selectedStageIds = serializers.SerializerMethodField()
    selected_stage_ids = serializers.SerializerMethodField()
    capacityKw = serializers.SerializerMethodField()
    capacity_kw = serializers.FloatField()
    fuelType = serializers.SerializerMethodField()
    fuel_type = serializers.CharField()
    efficiency_percent = serializers.FloatField(allow_null=True, required=False)
    basePrice = serializers.SerializerMethodField()
    base_price = serializers.FloatField()
    warranty_type_id = serializers.SerializerMethodField()
    status = serializers.CharField()
    createdDate = serializers.SerializerMethodField()
    created_at = serializers.DateTimeField()
    updatedDate = serializers.SerializerMethodField()
    updated_at = serializers.DateTimeField()

    def get_modelName(self, obj):
        return obj.name

    def get_internalCode(self, obj):
        return obj.model_code

    def get_code(self, obj):
        return obj.model_code

    def get_recipeId(self, obj):
        return obj.recipe.id if getattr(obj, 'recipe', None) else ""

    def get_recipe_id(self, obj):
        return obj.recipe.id if getattr(obj, 'recipe', None) else ""

    def get_selectedStageIds(self, obj):
        return obj.selected_stage_ids or []

    def get_selected_stage_ids(self, obj):
        return obj.selected_stage_ids or []

    def get_capacityKw(self, obj):
        return float(obj.capacity_kw or 50.0)

    def get_fuelType(self, obj):
        return obj.fuel_type or "GAS"

    def get_basePrice(self, obj):
        return float(obj.base_price or 0.0)

    def get_warranty_type_id(self, obj):
        return obj.warranty_type.id if getattr(obj, 'warranty_type', None) else ""

    def get_createdDate(self, obj):
        return obj.created_at.isoformat() if getattr(obj, 'created_at', None) else ""

    def get_updatedDate(self, obj):
        return obj.updated_at.isoformat() if getattr(obj, 'updated_at', None) else ""
