from rest_framework import serializers

class StockResponseSerializer(serializers.Serializer):
    id = serializers.CharField()
    warehouse_id = serializers.CharField()
    warehouse_name = serializers.SerializerMethodField()
    product_id = serializers.CharField()
    product_code = serializers.SerializerMethodField()
    product_name = serializers.SerializerMethodField()
    category_id = serializers.SerializerMethodField()
    category_name = serializers.SerializerMethodField()
    category = serializers.SerializerMethodField()
    material_type_id = serializers.SerializerMethodField()
    material_type_name = serializers.SerializerMethodField()
    material_type = serializers.SerializerMethodField()
    unit_id = serializers.SerializerMethodField()
    unit_name = serializers.SerializerMethodField()
    unit = serializers.SerializerMethodField()
    quantity = serializers.FloatField()
    reserved_quantity = serializers.FloatField()
    available_quantity = serializers.SerializerMethodField()
    avg_unit_cost = serializers.FloatField()
    updated_at = serializers.DateTimeField()

    def get_warehouse_name(self, obj):
        return obj.warehouse.name if getattr(obj, 'warehouse', None) else ""

    def get_product_code(self, obj):
        return obj.product.code if getattr(obj, 'product', None) else ""

    def get_product_name(self, obj):
        return obj.product.name if getattr(obj, 'product', None) else ""

    def get_category_id(self, obj):
        prod = getattr(obj, 'product', None)
        return prod.category.id if (prod and getattr(prod, 'category', None)) else ""

    def get_category_name(self, obj):
        prod = getattr(obj, 'product', None)
        return prod.category.name if (prod and getattr(prod, 'category', None)) else "Umumiy Kategoriya"

    def get_category(self, obj):
        prod = getattr(obj, 'product', None)
        if prod and getattr(prod, 'category', None):
            return {"id": prod.category.id, "name": prod.category.name, "code": prod.category.code}
        return {"id": "", "name": "Umumiy Kategoriya", "code": "GENERAL"}

    def get_material_type_id(self, obj):
        prod = getattr(obj, 'product', None)
        return prod.material_type.id if (prod and getattr(prod, 'material_type', None)) else ""

    def get_material_type_name(self, obj):
        prod = getattr(obj, 'product', None)
        return prod.material_type.name if (prod and getattr(prod, 'material_type', None)) else "Standart"

    def get_material_type(self, obj):
        prod = getattr(obj, 'product', None)
        if prod and getattr(prod, 'material_type', None):
            return {"id": prod.material_type.id, "name": prod.material_type.name, "code": prod.material_type.code}
        return {"id": "", "name": "Standart", "code": "STANDARD"}

    def get_unit_id(self, obj):
        prod = getattr(obj, 'product', None)
        return prod.unit.id if (prod and getattr(prod, 'unit', None)) else ""

    def get_unit_name(self, obj):
        prod = getattr(obj, 'product', None)
        return prod.unit.name if (prod and getattr(prod, 'unit', None)) else "dona"

    def get_unit(self, obj):
        prod = getattr(obj, 'product', None)
        if prod and getattr(prod, 'unit', None):
            return {"id": prod.unit.id, "name": prod.unit.name, "code": prod.unit.code, "symbol": getattr(prod.unit, 'symbol', '')}
        return {"id": "", "name": "dona", "code": "UNIT-PCS", "symbol": "dona"}

    def get_available_quantity(self, obj):
        return float(obj.quantity - obj.reserved_quantity)

class StockAdjustmentRequestSerializer(serializers.Serializer):
    warehouse_id = serializers.CharField(required=False, allow_null=True, allow_blank=True, default="")
    product_id = serializers.CharField(required=False, allow_null=True, allow_blank=True, default="")
    product_name = serializers.CharField(required=False, allow_null=True, allow_blank=True, default="")
    product_code = serializers.CharField(required=False, allow_null=True, allow_blank=True, default="")
    name = serializers.CharField(required=False, allow_null=True, allow_blank=True, default="")
    code = serializers.CharField(required=False, allow_null=True, allow_blank=True, default="")
    quantity = serializers.FloatField(required=False, allow_null=True, default=0.0)
    quantity_delta = serializers.FloatField(required=False, allow_null=True, default=0.0)
    unit_cost = serializers.FloatField(required=False, allow_null=True, default=0.0)
    movement_type = serializers.CharField(required=False, allow_null=True, allow_blank=True, default="ADJUSTMENT")
    notes = serializers.CharField(required=False, allow_null=True, allow_blank=True, default="")
