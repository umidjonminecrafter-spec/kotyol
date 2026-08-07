from django.db import models
from core.base_model import BaseModel


class Organization(BaseModel):
    name = models.CharField(max_length=255)
    description = models.CharField(max_length=500, null=True, blank=True)

    class Meta:
        db_table = 'organizations'


class Branch(BaseModel):
    organization = models.ForeignKey('Organization', on_delete=models.CASCADE, db_column='organization_id', related_name='branches')
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=50)
    address = models.CharField(max_length=255, null=True, blank=True)
    phone = models.CharField(max_length=50, null=True, blank=True)

    class Meta:
        db_table = 'branches'


class Position(BaseModel):
    code = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=255)
    description = models.CharField(max_length=500, null=True, blank=True)
    permissions = models.CharField(max_length=2000, null=True, blank=True)

    class Meta:
        db_table = 'positions'


class User(BaseModel):
    username = models.CharField(max_length=100, unique=True, db_index=True)
    hashed_password = models.CharField(max_length=255)
    full_name = models.CharField(max_length=255)
    phone = models.CharField(max_length=50, null=True, blank=True)
    role = models.CharField(max_length=50, default='EMPLOYEE')
    position = models.ForeignKey('Position', on_delete=models.SET_NULL, null=True, blank=True,
                                 db_column='position_id', related_name='users')
    department = models.CharField(max_length=100, null=True, blank=True)
    organization_name = models.CharField(max_length=255, null=True, blank=True)
    branch_name = models.CharField(max_length=255, null=True, blank=True)

    # Proper relations for multi-branch switching
    organization = models.ForeignKey('Organization', on_delete=models.SET_NULL, null=True, blank=True,
                                     db_column='organization_id_fk', related_name='users')
    branch = models.ForeignKey('Branch', on_delete=models.SET_NULL, null=True, blank=True,
                               db_column='branch_id_fk', related_name='users')

    salary_amount = models.CharField(max_length=50, null=True, blank=True)
    salary_type_id = models.CharField(max_length=36, null=True, blank=True)
    hire_date = models.CharField(max_length=50, null=True, blank=True)

    class Meta:
        db_table = 'users'

    # Non-persisted field set by authentication
    @property
    def is_anonymous(self):
        return False

    @property
    def is_authenticated(self):
        return True


class UserSession(BaseModel):
    user = models.ForeignKey('User', on_delete=models.CASCADE, db_column='user_id', related_name='sessions')
    refresh_token = models.CharField(max_length=500, db_index=True)
    user_agent = models.CharField(max_length=500, null=True, blank=True)
    ip_address = models.CharField(max_length=45, null=True, blank=True)
    expires_at = models.CharField(max_length=100)

    class Meta:
        db_table = 'user_sessions'
