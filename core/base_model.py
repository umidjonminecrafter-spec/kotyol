import uuid
from django.db import models
from django.utils import timezone


def generate_uuid():
    return str(uuid.uuid4())


class BaseModel(models.Model):
    id = models.CharField(max_length=36, primary_key=True, default=generate_uuid, editable=False)
    status = models.CharField(max_length=20, default='ACTIVE')
    is_active = models.BooleanField(default=True)

    organization_id = models.CharField(max_length=36, null=True, blank=True)
    branch_id = models.CharField(max_length=36, null=True, blank=True)

    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

    created_by_id = models.CharField(max_length=36, null=True, blank=True)
    updated_by_id = models.CharField(max_length=36, null=True, blank=True)

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        self.updated_at = timezone.now()
        super().save(*args, **kwargs)
