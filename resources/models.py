from django.db import models
from academics.models import Subject
from accounts.models import CR


class Resource(models.Model):

    title = models.CharField(
        max_length=200
    )

    description = models.TextField(
        blank=True
    )

    file_url = models.URLField()

    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE
    )

    uploaded_by = models.ForeignKey(
        CR,
        on_delete=models.CASCADE
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return self.title


class StoredFile(models.Model):
    file_name = models.CharField(max_length=255)
    file_url = models.CharField(max_length=500)
    bucket_name = models.CharField(max_length=100)
    mime_type = models.CharField(max_length=100)
    size = models.IntegerField()
    uploaded_at = models.DateTimeField(auto_now_add=True)
    version = models.IntegerField(default=1)
    uploaded_by = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.file_name} (v{self.version})"


class ResourceLibrary(models.Model):
    class ResourceType(models.TextChoices):
        NOTES = 'NOTES', 'Notes'
        PPT = 'PPT', 'Presentation'
        QUESTION_BANK = 'QUESTION_BANK', 'Question Bank'
        PREVIOUS_PAPER = 'PREVIOUS_PAPER', 'Previous Paper'
        SYLLABUS = 'SYLLABUS', 'Syllabus'
        LAB_MANUAL = 'LAB_MANUAL', 'Lab Manual'
        ASSIGNMENT = 'ASSIGNMENT', 'Assignment'
        TIMETABLE = 'TIMETABLE', 'Timetable'
        ACADEMIC_CALENDAR = 'ACADEMIC_CALENDAR', 'Academic Calendar'

    semester = models.ForeignKey('academics.Semester', on_delete=models.CASCADE, related_name='resources')
    subject = models.ForeignKey('academics.SemesterSubject', on_delete=models.CASCADE, related_name='resources')
    file = models.ForeignKey(StoredFile, on_delete=models.CASCADE, related_name='library_mappings')
    resource_type = models.CharField(max_length=50, choices=ResourceType.choices)

    class Meta:
        verbose_name_plural = "Resource Library Entries"

    def __str__(self):
        return f"{self.resource_type} - {self.file.file_name}"

