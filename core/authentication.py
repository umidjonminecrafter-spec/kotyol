from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from core.security import decode_token


class JWTAuthentication(BaseAuthentication):
    """
    JWT token authentication for DRF.
    Reads Bearer token from Authorization header, decodes it,
    and returns the User object.
    """

    def authenticate(self, request):
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        if not auth_header.startswith('Bearer '):
            return None

        token = auth_header[7:]
        payload = decode_token(token)

        if not payload or payload.get('type') != 'access':
            raise AuthenticationFailed("Token yaroqsiz yoki muddati o'tgan")

        user_id = payload.get('sub')
        if not user_id:
            raise AuthenticationFailed('Token sub identifikatori mavjud emas')

        from apps.accounts.models import User
        try:
            user = User.objects.get(id=user_id, status='ACTIVE')
        except User.DoesNotExist:
            raise AuthenticationFailed('Foydalanuvchi topilmadi yoki faol emas')

        # Set active branch from header or database default
        active_branch = request.META.get('HTTP_X_BRANCH_ID')
        user.active_branch_id = active_branch or getattr(user, 'branch_id', None)

        return (user, token)

    def authenticate_header(self, request):
        return 'Bearer'
