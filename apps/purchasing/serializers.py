from rest_framework import serializers

class PurchaseItemCreateSerializer(serializers.Serializer):
    product_id = serializers.CharField()
    quantity = serializers.FloatField(min_value=0.0001)
    unit_price = serializers.FloatField(min_value=0.0)

class PurchaseItemResponseSerializer(serializers.Serializer):
    id = serializers.CharField()
    product_id = serializers.CharField()
    product_code = serializers.SerializerMethodField()
    product_name = serializers.SerializerMethodField()
    quantity = serializers.FloatField()
    unit_price = serializers.FloatField()
    total_price = serializers.FloatField()

    def get_product_code(self, obj):
        return obj.product.code if getattr(obj, 'product', None) else None

    def get_product_name(self, obj):
        return obj.product.name if getattr(obj, 'product', None) else None

class PurchaseCreateSerializer(serializers.Serializer):
    purchase_number = serializers.CharField(required=False, allow_null=True, allow_blank=True, default="")
    supplier_id = serializers.CharField(required=False, allow_null=True, allow_blank=True, default="")
    supplier_name = serializers.CharField(required=False, allow_null=True, allow_blank=True, default="")
    warehouse_id = serializers.CharField(required=False, allow_null=True, allow_blank=True, default="")
    invoice_number = serializers.CharField(required=False, allow_null=True, allow_blank=True, default="")
    order_date = serializers.DateField(required=False, allow_null=True, default=None)
    tax_amount = serializers.FloatField(required=False, allow_null=True, default=0.0)
    total_amount = serializers.FloatField(required=False, allow_null=True, default=0.0)
    exchange_rate_at_creation = serializers.FloatField(required=False, allow_null=True, default=1.0)
    notes = serializers.CharField(required=False, allow_null=True, allow_blank=True, default="")
    status = serializers.CharField(required=False, allow_null=True, allow_blank=True, default="PENDING")
    items = PurchaseItemCreateSerializer(many=True, required=False, default=[])

class PurchaseUpdateStatusSerializer(serializers.Serializer):
    status = serializers.CharField()  # 'APPROVED', 'RECEIVED', 'CANCELLED'

class PurchaseResponseSerializer(serializers.Serializer):
    id = serializers.CharField()
    purchase_number = serializers.CharField()
    supplier_id = serializers.CharField()
    supplier_name = serializers.SerializerMethodField()
    warehouse_id = serializers.CharField()
    warehouse_name = serializers.SerializerMethodField()
    invoice_number = serializers.CharField(allow_null=True, required=False)
    order_date = serializers.DateField()
    subtotal = serializers.FloatField()
    tax_amount = serializers.FloatField()
    total_amount = serializers.FloatField()
    exchange_rate_at_creation = serializers.FloatField()
    status = serializers.CharField()
    created_at = serializers.DateTimeField()
    items = PurchaseItemResponseSerializer(many=True, required=False, default=[])

    def get_supplier_name(self, obj):
        return obj.supplier.name if getattr(obj, 'supplier', None) else None

    def get_warehouse_name(self, obj):
        return obj.warehouse.name if getattr(obj, 'warehouse', None) else None
