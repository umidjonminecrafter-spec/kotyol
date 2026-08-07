from django.db import models

class AuditLog(models.Model):
    id = models.CharField(max_length=36, primary_key=True)
    actor = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True, blank=True, db_column='actor_id', related_name='audit_logs')
    action = models.CharField(max_length=50)
    entity_name = models.CharField(max_length=100)
    entity_id = models.CharField(max_length=100)
    old_values = models.JSONField(null=True, blank=True)
    new_values = models.JSONField(null=True, blank=True)
    ip_address = models.CharField(max_length=45, null=True, blank=True)
    user_agent = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'audit_logs'
