from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator
from colleges.models import College
from academics.models import Department, Semester, Branch, Section, SemesterSubject


class User(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = 'ADMIN', 'Admin'
        CR = 'CR', 'Class Representative'
        STUDENT = 'STUDENT', 'Student'

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.STUDENT
    )

    email = models.EmailField(unique=True)


class Student(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='student_profile'
    )

    register_number = models.CharField(
        max_length=50,
        unique=True
    )

    name = models.CharField(
        max_length=150
    )

    email = models.EmailField(
        unique=True
    )

    phone = models.CharField(
        max_length=15,
        blank=True
    )

    college = models.ForeignKey(
        College,
        on_delete=models.CASCADE
    )

    department = models.ForeignKey(
        Department,
        on_delete=models.CASCADE
    )

    branch = models.ForeignKey(
        Branch,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    section = models.ForeignKey(
        Section,
        on_delete=models.CASCADE,
        null=True,
        blank=True
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
        return self.name

    def get_daily_schedule(self, date=None):
        """
        Returns the timetable entries for this student on a given date (or weekday).
        """
        from django.utils import timezone
        from academics.models import SectionSemester, TimetableEntry
        if date is None:
            date = timezone.now().date()
        day_name = date.strftime('%A').upper()
        
        active_enrollment = self.enrollments.filter(is_active=True).first()
        sem = active_enrollment.semester if active_enrollment else self.semester
        if not sem:
            return TimetableEntry.objects.none()
            
        sec_sem = SectionSemester.objects.filter(
            semester=sem,
            branch=self.branch,
            section=self.section,
            is_active=True
        ).first()
        if not sec_sem:
            return TimetableEntry.objects.none()
            
        timetable = sec_sem.timetables.first()
        if not timetable:
            return TimetableEntry.objects.none()
            
        return timetable.entries.filter(day_of_week=day_name).order_by('period_number')


class CR(models.Model):
    student = models.OneToOneField(
        Student,
        on_delete=models.CASCADE
    )

    assigned_at = models.DateTimeField(
        auto_now_add=True
    )

    is_active = models.BooleanField(
        default=True
    )

    def __str__(self):
        return f"CR - {self.student.name}"


class CRAssignment(models.Model):
    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name='cr_assignments'
    )
    semester = models.ForeignKey(
        Semester,
        on_delete=models.CASCADE,
        related_name='cr_assignments'
    )
    branch = models.ForeignKey(
        Branch,
        on_delete=models.CASCADE
    )
    section = models.ForeignKey(
        Section,
        on_delete=models.CASCADE
    )
    assigned_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_crs'
    )
    assigned_date = models.DateTimeField(
        auto_now_add=True
    )
    end_date = models.DateTimeField(
        null=True,
        blank=True
    )
    is_active = models.BooleanField(
        default=True
    )

    def save(self, *args, **kwargs):
        # Auto-resolve hierarchy from semester
        if self.semester and not self.section:
            self.section = self.semester.section
            self.branch = self.section.branch
        super().save(*args, **kwargs)

    def __str__(self):
        return f"CR {self.student.name} - {self.semester}"

    def get_daily_schedule(self, date=None):
        """
        Returns the timetable entries for the section managed by this CR on a given date.
        """
        from django.utils import timezone
        from academics.models import SectionSemester, TimetableEntry
        if date is None:
            date = timezone.now().date()
        day_name = date.strftime('%A').upper()
        
        sec_sem = SectionSemester.objects.filter(
            semester=self.semester,
            branch=self.branch,
            section=self.section,
            is_active=True
        ).first()
        if not sec_sem:
            return TimetableEntry.objects.none()
            
        timetable = sec_sem.timetables.first()
        if not timetable:
            return TimetableEntry.objects.none()
            
        return timetable.entries.filter(day_of_week=day_name).order_by('period_number')


class SemesterEnrollment(models.Model):
    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name='enrollments'
    )
    semester = models.ForeignKey(
        Semester,
        on_delete=models.CASCADE,
        related_name='enrollments'
    )
    enrolled_at = models.DateTimeField(
        auto_now_add=True
    )
    is_active = models.BooleanField(
        default=True
    )
    gpa = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0.00), MaxValueValidator(10.00)]
    )
    performance_score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0.00), MaxValueValidator(100.00)]
    )
    completion_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0.00), MaxValueValidator(100.00)]
    )
    rank = models.IntegerField(
        null=True,
        blank=True
    )
    remarks = models.TextField(
        blank=True
    )

    class Meta:
        unique_together = ('student', 'semester')

    def __str__(self):
        return f"{self.student.name} in {self.semester}"


class JoinSemesterRequest(models.Model):
    class RequestStatus(models.TextChoices):
        PENDING = 'PENDING', 'Pending'
        APPROVED = 'APPROVED', 'Approved'
        REJECTED = 'REJECTED', 'Rejected'

    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name='join_requests'
    )
    college = models.ForeignKey(
        College,
        on_delete=models.CASCADE
    )
    department = models.ForeignKey(
        Department,
        on_delete=models.CASCADE
    )
    branch = models.ForeignKey(
        Branch,
        on_delete=models.CASCADE
    )
    section = models.ForeignKey(
        Section,
        on_delete=models.CASCADE
    )
    semester = models.ForeignKey(
        Semester,
        on_delete=models.CASCADE
    )
    status = models.CharField(
        max_length=20,
        choices=RequestStatus.choices,
        default=RequestStatus.PENDING
    )
    remarks = models.TextField(
        blank=True
    )
    created_at = models.DateTimeField(
        auto_now_add=True
    )
    updated_at = models.DateTimeField(
        auto_now=True
    )
    reviewed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reviewed_requests'
    )

    def __str__(self):
        return f"{self.student.name} Join Request for {self.semester} ({self.status})"


class SubjectProgress(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='subject_progress')
    semester_subject = models.ForeignKey(SemesterSubject, on_delete=models.CASCADE, related_name='student_progress')
    completion_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    ai_assignments_completed = models.IntegerField(default=0)
    total_ai_assignments = models.IntegerField(default=0)
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('student', 'semester_subject')

    def __str__(self):
        return f"{self.student.name} - {self.semester_subject.subject_catalog.name} Progress"


class SemesterProgress(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='semester_progress')
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE, related_name='student_progress')
    overall_progress = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    completed_subjects = models.IntegerField(default=0)
    total_subjects = models.IntegerField(default=0)
    generated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('student', 'semester')

    def __str__(self):
        return f"{self.student.name} - Semester {self.semester.semester_number} Progress"


class SemesterReport(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='semester_reports')
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE, related_name='semester_reports')
    cgpa = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)
    performance_score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    assignments_completed = models.IntegerField(default=0)
    ai_assignments_completed = models.IntegerField(default=0)
    strengths = models.TextField(blank=True)
    weak_subjects = models.TextField(blank=True)
    generated_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('student', 'semester')

    def __str__(self):
        return f"Report {self.student.name} - Semester {self.semester.semester_number}"


class Faculty(models.Model):
    name = models.CharField(max_length=150)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15, blank=True)
    designation = models.CharField(max_length=100, blank=True)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='faculty_members')
    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='faculty_profile')

    class Meta:
        verbose_name_plural = "Faculty Members"

    def __str__(self):
        return f"{self.designation} {self.name}"



