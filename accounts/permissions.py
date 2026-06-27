from rest_framework.authentication import BaseAuthentication
from rest_framework import exceptions, permissions
from django.contrib.auth import get_user_model
from .utils import TokenService

User = get_user_model()


class JWTAuthentication(BaseAuthentication):
    """
    Custom authentication using cryptographically signed Bearer tokens.
    """
    def authenticate(self, request):
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return None

        parts = auth_header.split()
        if len(parts) != 2 or parts[0].lower() != 'bearer':
            raise exceptions.AuthenticationFailed('Authorization header must be Bearer <token>')

        token = parts[1]
        payload = TokenService.verify_token(token)

        try:
            user = User.objects.get(id=payload['user_id'])
        except User.DoesNotExist:
            raise exceptions.AuthenticationFailed('User not found')

        if not user.is_active:
            raise exceptions.AuthenticationFailed('User is inactive')

        return (user, token)


class IsStudent(permissions.BasePermission):
    """
    Permission check restricting access to students.
    """
    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and 
            request.user.role == User.Role.STUDENT
        )


class IsCR(permissions.BasePermission):
    """
    Permission check restricting access to Class Representatives (CRs).
    """
    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and 
            request.user.role == User.Role.CR
        )
