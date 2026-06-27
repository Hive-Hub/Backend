from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import SemesterSubject, Subject


from .models import SemesterSubject, Subject, Timetable


@receiver(post_save, sender=SemesterSubject)
def sync_legacy_subject(sender, instance, created, **kwargs):
    """
    Keep legacy Subject table in sync when SemesterSubject is mapped.
    This guarantees that older endpoints and queries pointing to Subject don't break.
    """
    if created:
        Subject.objects.get_or_create(
            semester=instance.semester,
            name=instance.subject_catalog.name,
            code=instance.subject_catalog.code,
            defaults={"credits": instance.subject_catalog.credits}
        )


@receiver(post_save, sender=Timetable)
def process_timetable_on_save(sender, instance, created, **kwargs):
    """
    Triggers AI extraction and population of TimetableEntry records when a Timetable is created
    or saved without existing entries.
    """
    from academics.services import populate_timetable_from_pdf
    if created or not instance.entries.exists():
        populate_timetable_from_pdf(instance)
