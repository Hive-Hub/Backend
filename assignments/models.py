from django.db import models
from academics.models import Subject, SemesterSubject, DailyClassReview
from accounts.models import CR, Student


class Assignment(models.Model):
    class AssignmentType(models.TextChoices):
        COLLEGE = 'COLLEGE', 'College'
        AI_GENERATED = 'AI_GENERATED', 'AI Generated'

    class Difficulty(models.TextChoices):
        EASY = 'EASY', 'Easy'
        MEDIUM = 'MEDIUM', 'Medium'
        HARD = 'HARD', 'Hard'

    title = models.CharField(
        max_length=200
    )

    description = models.TextField()

    deadline = models.DateTimeField()

    # Legacy ForeignKey preserved
    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    # Upgraded ForeignKey to point to SemesterSubject
    semester_subject = models.ForeignKey(
        SemesterSubject,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='assignments'
    )

    # Legacy ForeignKey preserved (nullable in case of automated creation)
    created_by = models.ForeignKey(
        CR,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    assignment_type = models.CharField(
        max_length=20,
        choices=AssignmentType.choices,
        default=AssignmentType.COLLEGE
    )

    external_link = models.URLField(
        max_length=500,
        blank=True
    )

    start_date = models.DateTimeField(
        null=True,
        blank=True
    )

    end_date = models.DateTimeField(
        null=True,
        blank=True
    )

    # AI Generated Properties
    generated_from_review = models.ForeignKey(
        DailyClassReview,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='ai_assignments'
    )

    difficulty = models.CharField(
        max_length=20,
        choices=Difficulty.choices,
        default=Difficulty.MEDIUM
    )

    topic = models.CharField(
        max_length=200,
        blank=True
    )

    generated_questions = models.JSONField(
        default=list,
        blank=True
    )

    def __str__(self):
        return self.title


class QuestionBank(models.Model):
    class QuestionType(models.TextChoices):
        MCQ = 'MCQ', 'Multiple Choice'
        SHORT = 'SHORT', 'Short Answer'
        LONG = 'LONG', 'Long Answer'
        CODING = 'CODING', 'Coding'

    class Difficulty(models.TextChoices):
        EASY = 'EASY', 'Easy'
        MEDIUM = 'MEDIUM', 'Medium'
        HARD = 'HARD', 'Hard'

    subject = models.ForeignKey(
        SemesterSubject,
        on_delete=models.CASCADE,
        related_name='question_bank'
    )
    topic = models.CharField(
        max_length=200
    )
    question_type = models.CharField(
        max_length=20,
        choices=QuestionType.choices
    )
    difficulty = models.CharField(
        max_length=20,
        choices=Difficulty.choices
    )
    question = models.TextField()
    answer = models.TextField()
    source_review = models.ForeignKey(
        DailyClassReview,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='questions'
    )
    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"{self.topic} ({self.question_type}) - {self.difficulty}"


class AssignmentSubmission(models.Model):
    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name='submissions'
    )
    assignment = models.ForeignKey(
        Assignment,
        on_delete=models.CASCADE,
        related_name='submissions'
    )
    completed_at = models.DateTimeField(
        auto_now_add=True
    )
    is_completed = models.BooleanField(
        default=True
    )
    score = models.IntegerField(
        null=True,
        blank=True
    )
    answers = models.JSONField(
        default=dict,
        blank=True
    )

    class Meta:
        unique_together = ('student', 'assignment')

    def __str__(self):
        return f"{self.student.name} - {self.assignment.title} Submission"

