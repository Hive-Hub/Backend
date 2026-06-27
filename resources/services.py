from django.db import transaction
from django.core.exceptions import ValidationError
from rest_framework import exceptions

from .models import Resource, StoredFile, ResourceLibrary
from accounts.models import Student, CR
from academics.models import Semester, SemesterSubject, Subject
from agents.services.storage_service import StorageService
from .validators import validate_resource_file


class ResourcesService:
    @staticmethod
    def upload_resource(cr_user, title, description, semester_id, subject_id, resource_type, file_obj):
        """
        Uploads resource file to Supabase, creates StoredFile, and registers it to ResourceLibrary.
        """
        try:
            student = Student.objects.get(user=cr_user)
            cr = CR.objects.get(student=student, is_active=True)
        except (Student.DoesNotExist, CR.DoesNotExist):
            raise exceptions.ValidationError("User is not an active CR.")

        try:
            semester = Semester.objects.get(id=semester_id)
            semester_subject = SemesterSubject.objects.get(id=subject_id, semester=semester)
        except (Semester.DoesNotExist, SemesterSubject.DoesNotExist):
            raise exceptions.ValidationError("Invalid Semester or Subject Catalog selection.")

        # Validate file
        validate_resource_file(file_obj.name)

        # Read file bytes
        file_bytes = file_obj.read()
        mime_type = file_obj.content_type
        file_name = file_obj.name

        # Perform upload
        res = StorageService.upload_file_to_supabase(
            file_name=file_name,
            file_bytes=file_bytes,
            mime_type=mime_type,
            bucket_name="StudentHub"
        )

        if not res.get("success"):
            raise exceptions.ValidationError(f"Supabase Storage upload failed: {res.get('error')}")

        with transaction.atomic():
            # Create StoredFile
            stored_file = StoredFile.objects.create(
                file_name=file_name,
                file_url=res["file_url"],
                bucket_name=res["bucket_name"],
                mime_type=mime_type,
                size=res["size"],
                uploaded_by=cr_user
            )

            # Create ResourceLibrary entry
            lib_entry = ResourceLibrary.objects.create(
                semester=semester,
                subject=semester_subject,
                file=stored_file,
                resource_type=resource_type
            )

            # Resolve legacy Subject FK constraint to create legacy Resource record
            legacy_subject = Subject.objects.filter(
                semester=semester,
                code=semester_subject.subject_catalog.code
            ).first()
            
            if not legacy_subject:
                # Fallback / create dummy legacy subject to satisfy constraint
                legacy_subject = Subject.objects.create(
                    semester=semester,
                    name=semester_subject.subject_catalog.name,
                    code=semester_subject.subject_catalog.code,
                    credits=semester_subject.subject_catalog.credits
                )

            # Create legacy Resource entry for backward compatibility
            Resource.objects.create(
                title=title or file_name,
                description=description,
                file_url=res["file_url"],
                subject=legacy_subject,
                uploaded_by=cr
            )

            return lib_entry
