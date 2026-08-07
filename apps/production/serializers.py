from rest_framework import serializers

class ProductionBatchCreateSerializer(serializers.Serializer):
    batch_number = serializers.CharField(required=False, allow_null=True, allow_blank=True, default="")
    production_number = serializers.CharField(required=False, allow_null=True, allow_blank=True, default="")
    boiler_id = serializers.CharField(required=False, allow_null=True, allow_blank=True, default="")
    product_name = serializers.CharField(required=False, allow_null=True, allow_blank=True, default="")
    target_quantity = serializers.IntegerField(required=False, allow_null=True, default=1)
    quantity = serializers.IntegerField(required=False, allow_null=True, default=1)
    start_date = serializers.DateField(required=False, allow_null=True, default=None)
    end_date = serializers.DateField(required=False, allow_null=True, default=None)
    notes = serializers.CharField(required=False, allow_null=True, allow_blank=True, default="")
    assigned_employees = serializers.ListField(child=serializers.CharField(), required=False, allow_null=True, default=[])

class ProductionBatchUpdateSerializer(serializers.Serializer):
    batch_number = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    production_number = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    boiler_id = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    target_quantity = serializers.IntegerField(required=False, allow_null=True)
    quantity = serializers.IntegerField(required=False, allow_null=True)
    completed_quantity = serializers.IntegerField(required=False, allow_null=True)
    defect_quantity = serializers.IntegerField(required=False, allow_null=True)
    status = serializers.CharField(required=False, allow_null=True)
    start_date = serializers.DateField(required=False, allow_null=True)
    end_date = serializers.DateField(required=False, allow_null=True)
    assigned_employees = serializers.ListField(child=serializers.CharField(), required=False, allow_null=True)

from apps.production.models import ProductionOperation

class ProductionOperationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductionOperation
        fields = ['id', 'operation_name', 'worker_id', 'worker_name', 'rate', 'status']

class ProductionBatchResponseSerializer(serializers.Serializer):
    id = serializers.CharField()
    batch_number = serializers.CharField()
    boiler_id = serializers.CharField()
    boiler_name = serializers.SerializerMethodField()
    target_quantity = serializers.IntegerField()
    completed_quantity = serializers.IntegerField()
    defect_quantity = serializers.IntegerField()
    start_date = serializers.DateField(allow_null=True, required=False)
    end_date = serializers.DateField(allow_null=True, required=False)
    status = serializers.CharField()
    created_at = serializers.DateTimeField()
    operations = serializers.SerializerMethodField()
    assigned_employees = serializers.SerializerMethodField()

    def get_boiler_name(self, obj):
        return obj.boiler.name if getattr(obj, 'boiler', None) else None

    def get_assigned_employees(self, obj):
        return [obj.assigned_employee] if getattr(obj, 'assigned_employee', None) else []

    def get_operations(self, obj):
        if not obj.operations.exists():
            default_ops = [
                {"name": "1. Ichki o'rxona va issiqlik almashtirgich qismini yig'ish", "rate": 150000, "worker": "Jasur Nazarov"},
                {"name": "2. Tashqi himoya korpusi va qoplamasini tayyorlash", "rate": 120000, "worker": "Alisher Karimov"},
                {"name": "3. O't yonish mexanizmi va gorelkasini o'rnatish", "rate": 180000, "worker": "Sardor Saidov"},
                {"name": "4. Payvandlash va germetik bosim sinovidan o'tkazish", "rate": 100000, "worker": "Jasur Nazarov"}
            ]
            for op in default_ops:
                ProductionOperation.objects.create(
                    batch=obj,
                    operation_name=op["name"],
                    rate=op["rate"],
                    worker_name=op["worker"],
                    status="PENDING"
                )
        return ProductionOperationSerializer(obj.operations.all(), many=True).data
