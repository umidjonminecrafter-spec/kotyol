from rest_framework import serializers

class TransactionCreateSerializer(serializers.Serializer):
    transaction_number = serializers.CharField(required=False, allow_null=True, allow_blank=True, default="")
    type = serializers.CharField(required=False, allow_null=True, allow_blank=True, default="INCOME")
    expense_type_id = serializers.CharField(required=False, allow_null=True, allow_blank=True, default="")
    amount = serializers.FloatField(required=False, allow_null=True, default=0.0)
    currency = serializers.CharField(required=False, allow_null=True, allow_blank=True, default="USD")
    reference_id = serializers.CharField(required=False, allow_null=True, allow_blank=True, default="")
    transaction_date = serializers.DateField(required=False, allow_null=True, default=None)
    notes = serializers.CharField(required=False, allow_null=True, allow_blank=True, default="")
    description = serializers.CharField(required=False, allow_null=True, allow_blank=True, default="")

class TransactionResponseSerializer(serializers.Serializer):
    id = serializers.CharField()
    transaction_number = serializers.CharField()
    type = serializers.CharField()
    expense_type_id = serializers.CharField(allow_null=True, required=False)
    amount = serializers.FloatField()
    currency = serializers.CharField()
    reference_id = serializers.CharField(allow_null=True, required=False)
    transaction_date = serializers.DateField()
    notes = serializers.CharField(allow_null=True, required=False)
    created_at = serializers.DateTimeField()
