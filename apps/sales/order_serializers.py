from rest_framework import serializers

class OrderCreateSerializer(serializers.Serializer):
    order_number = serializers.CharField(required=False, allow_null=True, allow_blank=True, default="")
    order_name = serializers.CharField(required=False, allow_null=True, allow_blank=True, default="")
    orderName = serializers.CharField(required=False, allow_null=True, allow_blank=True, default="")
    customer_id = serializers.CharField(required=False, allow_null=True, allow_blank=True, default="")
    customer_name = serializers.CharField(required=False, allow_null=True, allow_blank=True, default="")
    customerName = serializers.CharField(required=False, allow_null=True, allow_blank=True, default="")
    boiler_id = serializers.CharField(required=False, allow_null=True, allow_blank=True, default="")
    boiler_model_name = serializers.CharField(required=False, allow_null=True, allow_blank=True, default="")
    boilerModelName = serializers.CharField(required=False, allow_null=True, allow_blank=True, default="")
    quantity = serializers.FloatField(required=False, allow_null=True, default=1.0)
    unit_price = serializers.FloatField(required=False, allow_null=True, default=0.0)
    unitPrice = serializers.FloatField(required=False, allow_null=True, default=0.0)
    total_amount = serializers.FloatField(required=False, allow_null=True, default=0.0)
    totalAmount = serializers.FloatField(required=False, allow_null=True, default=0.0)
    deposit_amount = serializers.FloatField(required=False, allow_null=True, default=0.0)
    depositAmount = serializers.FloatField(required=False, allow_null=True, default=0.0)
    priority = serializers.CharField(required=False, allow_null=True, allow_blank=True, default="HIGH")
    status = serializers.CharField(required=False, allow_null=True, allow_blank=True, default="NEW")
    delivery_date = serializers.CharField(required=False, allow_null=True, allow_blank=True, default="")
    deliveryDate = serializers.CharField(required=False, allow_null=True, allow_blank=True, default="")
    expected_delivery_date = serializers.CharField(required=False, allow_null=True, allow_blank=True, default="")
    expectedDeliveryDate = serializers.CharField(required=False, allow_null=True, allow_blank=True, default="")
    auto_discount_on_late = serializers.BooleanField(required=False, default=True)
    autoDiscountOnLate = serializers.BooleanField(required=False, default=True)
    late_discount_rate = serializers.FloatField(required=False, allow_null=True, default=0.5)
    lateDiscountRate = serializers.FloatField(required=False, allow_null=True, default=0.5)
    assigned_employee_id = serializers.CharField(required=False, allow_null=True, allow_blank=True, default="")
    assignedEmployeeId = serializers.CharField(required=False, allow_null=True, allow_blank=True, default="")
    assigned_employee_name = serializers.CharField(required=False, allow_null=True, allow_blank=True, default="")
    assignedEmployeeName = serializers.CharField(required=False, allow_null=True, allow_blank=True, default="")
    notes = serializers.CharField(required=False, allow_null=True, allow_blank=True, default="")

class OrderResponseSerializer(serializers.Serializer):
    id = serializers.CharField()
    order_number = serializers.CharField()
    orderNumber = serializers.SerializerMethodField()
    order_name = serializers.SerializerMethodField()
    orderName = serializers.SerializerMethodField()
    customer_id = serializers.SerializerMethodField()
    customerId = serializers.SerializerMethodField()
    customer_name = serializers.SerializerMethodField()
    customerName = serializers.SerializerMethodField()
    boiler_id = serializers.SerializerMethodField()
    boilerId = serializers.SerializerMethodField()
    boiler_model_name = serializers.SerializerMethodField()
    boilerModelName = serializers.SerializerMethodField()
    quantity = serializers.FloatField()
    unit_price = serializers.FloatField()
    unitPrice = serializers.SerializerMethodField()
    total_amount = serializers.FloatField()
    totalAmount = serializers.SerializerMethodField()
    deposit_amount = serializers.SerializerMethodField()
    depositAmount = serializers.SerializerMethodField()
    priority = serializers.CharField()
    status = serializers.CharField()
    delivery_date = serializers.SerializerMethodField()
    deliveryDate = serializers.SerializerMethodField()
    expected_delivery_date = serializers.SerializerMethodField()
    expectedDeliveryDate = serializers.SerializerMethodField()
    auto_discount_on_late = serializers.SerializerMethodField()
    autoDiscountOnLate = serializers.SerializerMethodField()
    late_discount_rate = serializers.SerializerMethodField()
    lateDiscountRate = serializers.SerializerMethodField()
    assigned_employee_id = serializers.SerializerMethodField()
    assignedEmployeeId = serializers.SerializerMethodField()
    assigned_employee_name = serializers.SerializerMethodField()
    assignedEmployeeName = serializers.SerializerMethodField()
    notes = serializers.CharField(allow_null=True, required=False)
    created_at = serializers.DateTimeField()
    updated_at = serializers.DateTimeField()

    def get_orderNumber(self, obj):
        return obj.order_number

    def get_order_name(self, obj):
        return obj.order_name or ""

    def get_orderName(self, obj):
        return obj.order_name or ""

    def get_customer_id(self, obj):
        return obj.customer.id if getattr(obj, 'customer', None) else ""

    def get_customerId(self, obj):
        return obj.customer.id if getattr(obj, 'customer', None) else ""

    def get_customer_name(self, obj):
        if getattr(obj, 'customer', None):
            return obj.customer.name
        return obj.customer_name or ""

    def get_customerName(self, obj):
        return self.get_customer_name(obj)

    def get_boiler_id(self, obj):
        return obj.boiler.id if getattr(obj, 'boiler', None) else ""

    def get_boilerId(self, obj):
        return obj.boiler.id if getattr(obj, 'boiler', None) else ""

    def get_boiler_model_name(self, obj):
        if getattr(obj, 'boiler', None):
            return obj.boiler.name
        return obj.boiler_model_name or ""

    def get_boilerModelName(self, obj):
        return self.get_boiler_model_name(obj)

    def get_unitPrice(self, obj):
        return float(obj.unit_price or 0.0)

    def get_totalAmount(self, obj):
        return float(obj.total_amount or 0.0)

    def get_deposit_amount(self, obj):
        return float(getattr(obj, 'deposit_amount', 0.0) or 0.0)

    def get_depositAmount(self, obj):
        return self.get_deposit_amount(obj)

    def get_delivery_date(self, obj):
        d = getattr(obj, 'delivery_date', None)
        if not d:
            return ""
        if isinstance(d, str):
            return d
        return d.isoformat() if hasattr(d, 'isoformat') else str(d)

    def get_deliveryDate(self, obj):
        return self.get_delivery_date(obj)

    def get_expected_delivery_date(self, obj):
        return self.get_delivery_date(obj)

    def get_expectedDeliveryDate(self, obj):
        return self.get_delivery_date(obj)

    def get_auto_discount_on_late(self, obj):
        val = getattr(obj, 'auto_discount_on_late', True)
        return True if val is None else bool(val)

    def get_autoDiscountOnLate(self, obj):
        return self.get_auto_discount_on_late(obj)

    def get_late_discount_rate(self, obj):
        return float(getattr(obj, 'late_discount_rate', 0.5) or 0.5)

    def get_lateDiscountRate(self, obj):
        return self.get_late_discount_rate(obj)

    def get_assigned_employee_id(self, obj):
        return getattr(obj, 'assigned_employee_id', '') or ''

    def get_assignedEmployeeId(self, obj):
        return self.get_assigned_employee_id(obj)

    def get_assigned_employee_name(self, obj):
        return getattr(obj, 'assigned_employee_name', '') or ''

    def get_assignedEmployeeName(self, obj):
        return self.get_assigned_employee_name(obj)
