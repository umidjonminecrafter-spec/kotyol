from rest_framework import serializers

class SaleCreateSerializer(serializers.Serializer):
    invoice_number = serializers.CharField(required=False, allow_null=True, allow_blank=True, default="")
    customer_id = serializers.CharField(required=False, allow_null=True, allow_blank=True, default="")
    boiler_id = serializers.CharField(required=False, allow_null=True, allow_blank=True, default="")
    product_id = serializers.CharField(required=False, allow_null=True, allow_blank=True, default="")
    quantity = serializers.FloatField(required=False, allow_null=True, default=1.0)
    unit_price = serializers.FloatField(required=False, allow_null=True, default=0.0)
    discount_amount = serializers.FloatField(required=False, allow_null=True, default=0.0)
    tax_amount = serializers.FloatField(required=False, allow_null=True, default=0.0)
    exchange_rate_at_creation = serializers.FloatField(required=False, allow_null=True, default=1.0)
    payment_status = serializers.CharField(required=False, allow_null=True, allow_blank=True, default="UNPAID")
    delivery_status = serializers.CharField(required=False, allow_null=True, allow_blank=True, default="PENDING")
    assigned_employee_id = serializers.CharField(required=False, allow_null=True, allow_blank=True, default="")
    assigned_employee_name = serializers.CharField(required=False, allow_null=True, allow_blank=True, default="")
    warranty_period = serializers.CharField(required=False, allow_null=True, allow_blank=True, default="")
    warranty_start_date = serializers.DateField(required=False, allow_null=True)
    warranty_end_date = serializers.DateField(required=False, allow_null=True)
    delivery_location = serializers.CharField(required=False, allow_null=True, allow_blank=True, default="")
    notes = serializers.CharField(required=False, allow_null=True, allow_blank=True, default="")

class SaleUpdateStatusSerializer(serializers.Serializer):
    payment_status = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    delivery_status = serializers.CharField(required=False, allow_null=True, allow_blank=True)

class SaleResponseSerializer(serializers.Serializer):
    id = serializers.CharField()
    invoice_number = serializers.CharField()
    customer_id = serializers.SerializerMethodField()
    customer_name = serializers.SerializerMethodField()
    customer_phone = serializers.SerializerMethodField()
    customer_address = serializers.SerializerMethodField()
    customer_email = serializers.SerializerMethodField()
    boiler_id = serializers.SerializerMethodField()
    product_id = serializers.SerializerMethodField()
    quantity = serializers.FloatField()
    unit_price = serializers.FloatField()
    subtotal = serializers.FloatField()
    discount_amount = serializers.FloatField()
    tax_amount = serializers.FloatField()
    total_amount = serializers.FloatField()
    exchange_rate_at_creation = serializers.FloatField()
    payment_status = serializers.CharField()
    delivery_status = serializers.CharField()
    status = serializers.CharField(required=False, default="ACTIVE")
    created_at = serializers.DateTimeField()
    assigned_employee_id = serializers.CharField(allow_null=True, required=False)
    assigned_employee_name = serializers.CharField(allow_null=True, required=False)
    warranty_period = serializers.CharField(allow_null=True, required=False)
    warranty_start_date = serializers.DateField(allow_null=True, required=False)
    warranty_end_date = serializers.DateField(allow_null=True, required=False)
    delivery_location = serializers.CharField(allow_null=True, required=False)
    notes = serializers.CharField(allow_null=True, required=False)
    boiler_model_name = serializers.SerializerMethodField()

    def get_customer_id(self, obj):
        return obj.customer.id if getattr(obj, 'customer', None) else ""

    def get_customer_name(self, obj):
        return obj.customer.name if getattr(obj, 'customer', None) else ""

    def get_customer_phone(self, obj):
        return obj.customer.phone if getattr(obj, 'customer', None) else ""

    def get_customer_address(self, obj):
        return obj.customer.address if getattr(obj, 'customer', None) else ""

    def get_customer_email(self, obj):
        return obj.customer.email if getattr(obj, 'customer', None) else ""

    def get_boiler_id(self, obj):
        return obj.boiler.id if getattr(obj, 'boiler', None) else ""

    def get_product_id(self, obj):
        return obj.product.id if getattr(obj, 'product', None) else ""

    def get_boiler_model_name(self, obj):
        return obj.boiler.name if getattr(obj, 'boiler', None) else ""
