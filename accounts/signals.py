from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db import transaction
from .models import CRAssignment, CR, User, SemesterEnrollment


@receiver(post_save, sender=CRAssignment)
def sync_cr_legacy_and_role(sender, instance, created, **kwargs):
    """
    Ensure legacy CR model and User role are synced with active CRAssignments.
    """
    student = instance.student
    user = student.user

    def sync():
        active_assignments = CRAssignment.objects.filter(student=student, is_active=True)
        has_active = active_assignments.exists()

        with transaction.atomic():
            if has_active:
                # Sync User Model role to CR
                if user.role != User.Role.CR:
                    user.role = User.Role.CR
                    user.save(update_fields=['role'])
                
                # Sync Legacy CR Profile
                cr_profile, _ = CR.objects.get_or_create(student=student)
                if not cr_profile.is_active:
                    cr_profile.is_active = True
                    cr_profile.save(update_fields=['is_active'])
            else:
                # Sync User Model role back to STUDENT
                if user.role == User.Role.CR:
                    user.role = User.Role.STUDENT
                    user.save(update_fields=['role'])
                
                # Deactivate legacy CR Profile
                try:
                    cr_profile = CR.objects.get(student=student)
                    if cr_profile.is_active:
                        cr_profile.is_active = False
                        cr_profile.save(update_fields=['is_active'])
                except CR.DoesNotExist:
                    pass

    transaction.on_commit(sync)


@receiver(post_save, sender=SemesterEnrollment)
def sync_student_semester_id(sender, instance, created, **kwargs):
    """
    Ensure the deprecated student.semester field remains in sync with the active enrollment.
    """
    student = instance.student
    if instance.is_active:
        if student.semester != instance.semester:
            student.semester = instance.semester
            student.save(update_fields=['semester'])

