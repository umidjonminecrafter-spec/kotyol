from rest_framework import serializers

class LeadCreateSerializer(serializers.Serializer):
    full_name = serializers.CharField(required=True)
    phone = serializers.CharField(required=True)
    email = serializers.EmailField(required=False, allow_null=True, allow_blank=True, default='')
    company_name = serializers.CharField(required=False, allow_null=True, allow_blank=True, default='')
    status = serializers.CharField(required=False, default="NEW")
    source = serializers.CharField(required=False, allow_null=True, allow_blank=True, default='')
    notes = serializers.CharField(required=False, allow_null=True, allow_blank=True, default='')
    next_contact_date = serializers.DateField(required=False, allow_null=True)
    assigned_employee_id = serializers.CharField(required=False, allow_null=True, allow_blank=True, default='')
    assigned_employee_name = serializers.CharField(required=False, allow_null=True, allow_blank=True, default='')

class LeadResponseSerializer(serializers.Serializer):
    id = serializers.CharField()
    full_name = serializers.SerializerMethodField()
    phone = serializers.SerializerMethodField()
    email = serializers.SerializerMethodField()
    company_name = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()
    source = serializers.SerializerMethodField()
    notes = serializers.SerializerMethodField()
    next_contact_date = serializers.SerializerMethodField()
    assigned_employee_id = serializers.SerializerMethodField()
    assigned_employee_name = serializers.SerializerMethodField()
    created_at = serializers.DateTimeField()

    def get_full_name(self, obj):
        return getattr(obj, 'full_name', '') or ''

    def get_phone(self, obj):
        return getattr(obj, 'phone', '') or ''

    def get_email(self, obj):
        return getattr(obj, 'email', '') or ''

    def get_company_name(self, obj):
        return getattr(obj, 'company_name', '') or ''

    def get_status(self, obj):
        return getattr(obj, 'status', 'NEW') or 'NEW'

    def get_source(self, obj):
        return getattr(obj, 'source', '') or ''

    def get_notes(self, obj):
        return getattr(obj, 'notes', '') or ''

    def get_next_contact_date(self, obj):
        val = getattr(obj, 'next_contact_date', None)
        return str(val) if val else ''

    def get_assigned_employee_id(self, obj):
        return getattr(obj, 'assigned_employee_id', '') or ''

    def get_assigned_employee_name(self, obj):
        return getattr(obj, 'assigned_employee_name', '') or ''
