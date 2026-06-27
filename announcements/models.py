from django.db import models
from accounts.models import CR
from academics.models import Semester


class Announcement(models.Model):

    title = models.CharField(
        max_length=200
    )

    message = models.TextField()

    created_by = models.ForeignKey(
        CR,
        on_delete=models.CASCADE
    )

    semester = models.ForeignKey(
        Semester,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return self.title

