from django.core.exceptions import ValidationError
from django.utils import timezone


def validate_deadline_future(deadline):
    """
    Checks that the assignment deadline is in the future.
    """
    if deadline < timezone.now():
        raise ValidationError("Assignment deadline must be in the future.")
