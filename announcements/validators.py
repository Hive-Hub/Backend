from django.core.exceptions import ValidationError


def validate_announcement_length(message):
    """
    Validates announcement message length constraints.
    """
    if len(message) < 10:
        raise ValidationError("Announcement message must be at least 10 characters long.")
