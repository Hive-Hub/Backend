from rest_framework import permissions


class IsAgentAdminOrCRReadOnly(permissions.BasePermission):
    """
    Custom permission to restrict access to QISHub Agent Management System:
    - Admin (role='ADMIN', or staff/superuser) has full write/read access.
    - CR (role='CR') has read-only access.
    - Student (role='STUDENT') or any other user has no access.
    """

    def has_permission(self, request, view):
        # User must be authenticated
        if not request.user or not request.user.is_authenticated:
            return False

        # Support both the explicit 'role' field and django superuser/staff checks
        role = getattr(request.user, 'role', None)
        is_admin = (
            role == 'ADMIN' or 
            request.user.is_superuser or 
            request.user.is_staff
        )

        if is_admin:
            return True

        if role == 'CR':
            # CR has read-only access
            return request.method in permissions.SAFE_METHODS

        # Default block for STUDENT or any other role
        return False


class IsMonitoringObserverPermission(permissions.BasePermission):
    """
    Custom permission for telemetry and analytics views:
    - Admin (role='ADMIN') has full access.
    - CR (role='CR') and Student (role='STUDENT') have read-only access.
    """

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        role = getattr(request.user, 'role', None)
        is_admin = (
            role == 'ADMIN' or 
            request.user.is_superuser or 
            request.user.is_staff
        )

        if is_admin:
            return True

        if role in ['CR', 'STUDENT']:
            return request.method in permissions.SAFE_METHODS

        return False

