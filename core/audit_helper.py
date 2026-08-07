import uuid
import datetime
from decimal import Decimal

def _sanitize_for_json(obj):
    if isinstance(obj, dict):
        return {k: _sanitize_for_json(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [_sanitize_for_json(item) for item in obj]
    elif isinstance(obj, (datetime.date, datetime.datetime)):
        return obj.isoformat()
    elif isinstance(obj, Decimal):
        return float(obj)
    elif isinstance(obj, uuid.UUID):
        return str(obj)
    return obj

def record_audit_log(action, entity_name, entity_id, actor_id=None,
                     old_values=None, new_values=None, request=None):
    from apps.audit.models import AuditLog

    ip_address = None
    user_agent = None
    if request:
        ip_address = request.META.get('REMOTE_ADDR')
        user_agent = request.META.get('HTTP_USER_AGENT')

    AuditLog.objects.create(
        id=str(uuid.uuid4()),
        actor_id=actor_id,
        action=action,
        entity_name=entity_name,
        entity_id=str(entity_id),
        old_values=_sanitize_for_json(old_values) if old_values is not None else None,
        new_values=_sanitize_for_json(new_values) if new_values is not None else None,
        ip_address=ip_address,
        user_agent=user_agent,
    )
