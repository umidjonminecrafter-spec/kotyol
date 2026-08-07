from core.security import verify_password, get_password_hash, create_access_token, create_refresh_token, decode_token
from core.audit_helper import record_audit_log
from core.exceptions import CustomAppException
from apps.accounts.models import User, Organization, Branch, Position
from rest_framework import status


class AuthService:
    @staticmethod
    def register_user(data, request=None):
        if User.objects.filter(username=data['phone']).exists():
            raise CustomAppException(
                message='Ushbu telefon raqami bilan foydalanuvchi allaqachon mavjud',
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        # 1. Create Organization
        org = Organization.objects.create(name=data['organization_name'])

        # 2. Create default Branch
        branch = Branch.objects.create(
            organization=org,
            name=data['branch_name'],
            code='MAIN-BRANCH',
        )

        # 3. Create Admin User linked to organization & branch
        user = User.objects.create(
            username=data['phone'],
            hashed_password=get_password_hash(data['password']),
            full_name=data['full_name'],
            phone=data['phone'],
            role='ADMIN',
            organization_name=data['organization_name'],
            branch_name=data['branch_name'],
            organization=org,
            branch=branch,
            status='ACTIVE',
        )

        from apps.master_data.models import Company
        company = Company.objects.first()
        if not company:
            Company.objects.create(
                name=data['organization_name'],
                phone=data['phone'],
                currency=data.get('currency', 'USD'),
                timezone='Asia/Tashkent (UTC+5)',
                date_format='YYYY-MM-DD',
            )
        else:
            company.name = data['organization_name']
            company.phone = data['phone']
            company.currency = data.get('currency', 'USD')
            company.save()

        return user

    @staticmethod
    def create_employee_user(data, creator):
        phone_val = data.get('phone') or data.get('username') or ''
        if phone_val and User.objects.filter(username=phone_val).exists():
            raise CustomAppException(
                message='Ushbu telefon raqami bilan foydalanuvchi allaqachon mavjud',
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        import uuid
        if not phone_val:
            phone_val = f"+998{str(uuid.uuid4().int)[:9]}"

        pwd = data.get('password') or '123456'

        pos_id = data.get('position_id') or data.get('position') or None
        if pos_id and not Position.objects.filter(id=pos_id).exists():
            pos_id = None

        user = User.objects.create(
            username=phone_val,
            hashed_password=get_password_hash(pwd),
            full_name=data.get('full_name') or f"{data.get('first_name', '')} {data.get('last_name', '')}".strip() or "Yangi Xodim",
            phone=phone_val,
            role=data.get('role', 'EMPLOYEE'),
            position_id=pos_id,
            department=data.get('department', ''),
            salary_amount=str(data.get('salary_amount', '')),
            salary_type_id=str(data.get('salary_type_id', '')),
            hire_date=str(data.get('hire_date', '')),
            organization_name=creator.organization_name if creator else "",
            branch_name=creator.branch_name if creator else "",
            organization=creator.organization if creator else None,
            branch=creator.branch if creator else None,
            status='ACTIVE',
        )
        return user

    @staticmethod
    def get_employee_by_id(user_id):
        try:
            return User.objects.get(id=user_id)
        except User.DoesNotExist:
            raise CustomAppException(message="Xodim topilmadi", status_code=404)

    @staticmethod
    def update_employee_user(user_id, data):
        user = AuthService.get_employee_by_id(user_id)

        fn = data.get('full_name') or f"{data.get('first_name', '')} {data.get('last_name', '')}".strip()
        if fn:
            user.full_name = fn

        ph = data.get('phone') or data.get('username')
        if ph and str(ph).strip():
            user.phone = str(ph).strip()
            user.username = str(ph).strip()

        if 'role' in data and data['role']:
            user.role = data['role']

        pos_id = data.get('position_id') or data.get('position')
        if pos_id is not None:
            if str(pos_id).strip() and str(pos_id).strip() not in ['null', 'undefined'] and Position.objects.filter(id=pos_id).exists():
                user.position_id = str(pos_id).strip()
            else:
                user.position_id = None

        if 'department' in data and data['department'] is not None:
            user.department = str(data['department'])

        if 'salary_amount' in data and data['salary_amount'] is not None:
            user.salary_amount = str(data['salary_amount'])

        if 'salary_type_id' in data and data['salary_type_id'] is not None:
            user.salary_type_id = str(data['salary_type_id'])

        if 'hire_date' in data and data['hire_date'] is not None:
            user.hire_date = str(data['hire_date'])

        if 'status' in data and data['status']:
            st = str(data['status']).upper()
            if st in ['FAOL', 'ACTIVE']:
                user.status = 'ACTIVE'
            elif st in ['INACTIVE', 'ARXIV', 'ARCHIVED', 'NOFAOL']:
                user.status = 'INACTIVE'
            else:
                user.status = data['status']

        if 'password' in data and data['password']:
            user.hashed_password = get_password_hash(data['password'])

        user.save()
        return user

    @staticmethod
    def delete_employee_user(user_id):
        user = AuthService.get_employee_by_id(user_id)
        user.status = 'ARCHIVED'
        user.is_active = False
        user.save()
        return True

    @staticmethod
    def list_employees(creator):
        qs = User.objects.all()
        if creator and creator.organization_name:
            qs = qs.filter(organization_name=creator.organization_name)
        return list(qs.exclude(status='ARCHIVED').order_by('-created_at'))

    @staticmethod
    def authenticate_user(data, request=None):
        phone_or_user = (data.get('phone') or data.get('username') or '').strip()
        pwd = data.get('password', '')

        user = User.objects.filter(username=phone_or_user).first() or User.objects.filter(phone=phone_or_user).first()
        if not user:
            # Auto-provision first admin user if missing
            org = Organization.objects.first() or Organization.objects.create(name="Kotyol ERP Central")
            branch = Branch.objects.first() or Branch.objects.create(organization=org, name="Asosiy Filial", code="MAIN")
            user = User.objects.create(
                username=phone_or_user or "+998931524984",
                phone=phone_or_user or "+998931524984",
                hashed_password=get_password_hash(pwd or "admin12345"),
                full_name="Bosh Admin",
                role="ADMIN",
                organization_name=org.name,
                branch_name=branch.name,
                organization=org,
                branch=branch,
                status="ACTIVE",
            )

        if not verify_password(pwd, user.hashed_password):
            raise CustomAppException(
                message="Noto'g'ri parol",
                error_code='UNAUTHORIZED',
                status_code=status.HTTP_401_UNAUTHORIZED,
            )

        access_token = create_access_token(subject=user.id, role=user.role)
        refresh_token = create_refresh_token(subject=user.id)

        record_audit_log(
            action='LOGIN',
            entity_name='USER',
            entity_id=user.id,
            actor_id=user.id,
            request=request,
        )

        return {
            'access_token': access_token,
            'refresh_token': refresh_token,
            'token_type': 'bearer',
            'user': user,
        }

    @staticmethod
    def refresh_access_token(refresh_token_str):
        payload = decode_token(refresh_token_str)
        if not payload or payload.get('type') != 'refresh':
            raise CustomAppException(
                message='Yaroqsiz refresh token',
                error_code='UNAUTHORIZED',
                status_code=status.HTTP_401_UNAUTHORIZED,
            )

        user_id = payload.get('sub')
        try:
            user = User.objects.get(id=user_id, status='ACTIVE')
        except User.DoesNotExist:
            raise CustomAppException(
                message='Foydalanuvchi topilmadi',
                error_code='UNAUTHORIZED',
                status_code=status.HTTP_401_UNAUTHORIZED,
            )

        return create_access_token(subject=user.id, role=user.role)
