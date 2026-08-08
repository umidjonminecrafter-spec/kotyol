from rest_framework import serializers

class AuditLogResponseSerializer(serializers.Serializer):
    id = serializers.CharField()
    actor_id = serializers.CharField(allow_null=True, required=False)
    actor_name = serializers.SerializerMethodField()
    action = serializers.CharField()
    entity_name = serializers.CharField()
    entity_id = serializers.CharField()
    old_values = serializers.JSONField(allow_null=True, required=False)
    new_values = serializers.JSONField(allow_null=True, required=False)
    ip_address = serializers.CharField(allow_null=True, required=False)
    user_agent = serializers.CharField(allow_null=True, required=False)
    created_at = serializers.DateTimeField()

    def get_actor_name(self, obj):
        if hasattr(obj, 'actor') and obj.actor:
            return getattr(obj.actor, 'full_name', None) or getattr(obj.actor, 'username', None) or str(obj.actor_id)
        return str(obj.actor_id) if obj.actor_id else 'Tizim'
