import os
from django.core.exceptions import ValidationError


def validate_resource_file(file_name):
    """
    Ensures that uploaded resources are in allowed formats.
    """
    ext = os.path.splitext(file_name)[1].lower()
    allowed_extensions = ['.pdf', '.ppt', '.pptx', '.doc', '.docx', '.xls', '.xlsx', '.png', '.jpg', '.jpeg', '.zip']
    if ext not in allowed_extensions:
        raise ValidationError(f"File extension '{ext}' is not supported. Allowed formats: {', '.join(allowed_extensions)}")
