import time
import logging
from django.core import signing
from django.contrib.auth import get_user_model

logger = logging.getLogger(__name__)
User = get_user_model()


def success_response(data=None, message="Success", status_code=200):
    """
    Standard Success Response format
    """
    from rest_framework.response import Response
    return Response({
        "success": True,
        "message": message,
        "data": data or {}
    }, status=status_code)


def error_response(errors=None, message="Validation Error", status_code=400):
    """
    Standard Error/Validation Response format
    """
    from rest_framework.response import Response
    return Response({
        "success": False,
        "message": message,
        "errors": errors or {}
    }, status=status_code)


class TokenService:
    @staticmethod
    def generate_token(user):
        """
        Generates a secure, signed token string containing user identification.
        Expires after 24 hours.
        """
        payload = {
            'user_id': user.id,
            'email': user.email,
            'role': user.role,
            'timestamp': time.time()
        }
        return signing.dumps(payload, salt='qishub-jwt-salt')

    @staticmethod
    def verify_token(token):
        """
        Validates signed token. Raises AuthenticationFailed if invalid or expired.
        """
        from rest_framework import exceptions
        try:
            payload = signing.loads(token, salt='qishub-jwt-salt', max_age=86400)
            return payload
        except signing.SignatureExpired:
            raise exceptions.AuthenticationFailed('Token has expired')
        except signing.BadSignature:
            raise exceptions.AuthenticationFailed('Invalid token signature')
        except Exception as e:
            raise exceptions.AuthenticationFailed(f'Invalid token: {str(e)}')


def custom_exception_handler(exc, context):
    """
    Custom DRF exception handler standardizing success/failure envelopes.
    """
    from rest_framework.views import exception_handler
    from rest_framework import status
    
    response = exception_handler(exc, context)
    
    if response is not None:
        message = "Error occurred"
        if response.status_code == status.HTTP_400_BAD_REQUEST:
            message = "Validation Error"
        elif response.status_code == status.HTTP_401_UNAUTHORIZED:
            message = "Authentication Failed"
        elif response.status_code == status.HTTP_403_FORBIDDEN:
            message = "Permission Denied"
        elif response.status_code == status.HTTP_404_NOT_FOUND:
            message = "Resource Not Found"

        response.data = {
            "success": False,
            "message": response.data.get('detail', message) if isinstance(response.data, dict) else message,
            "errors": response.data
        }
    return response
