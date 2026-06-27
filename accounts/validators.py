import re
from django.core.exceptions import ValidationError


def validate_phone_number(value):
    """
    Validates phone formats (+123456789 or standard numbers).
    """
    pattern = r'^\+?1?\d{9,15}$'
    if not re.match(pattern, value):
        raise ValidationError("Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.")
