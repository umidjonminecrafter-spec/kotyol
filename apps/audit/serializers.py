from rest_framework import serializers

class AuditLogResponseSerializer(serializers.Serializer):
    id = serializers.CharField()
    actor_id = serializers.CharField(allow_null=True, required=False)
    action = serializers.CharField()
    entity_name = serializers.CharField()
    entity_id = serializers.CharField()
    old_values = serializers.JSONField(allow_null=True, required=False)
    new_values = serializers.JSONField(allow_null=True, required=False)
    ip_address = serializers.CharField(allow_null=True, required=False)
    user_agent = serializers.CharField(allow_null=True, required=False)
    created_at = serializers.DateTimeField()
