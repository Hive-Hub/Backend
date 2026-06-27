from django.db import models
from colleges.models import College


class Department(models.Model):
    college = models.ForeignKey(
        College,
        on_delete=models.CASCADE
    )

    name = models.CharField(max_length=100)

    code = models.CharField(
        max_length=20,
        unique=True
    )

    def __str__(self):
        return self.name


class Branch(models.Model):
    department = models.ForeignKey(
        Department,
        on_delete=models.CASCADE,
        related_name='branches'
    )

    name = models.CharField(max_length=100)

    code = models.CharField(
        max_length=20,
        unique=True
    )

    class Meta:
        verbose_name_plural = "Branches"

    def __str__(self):
        return f"{self.department.code} - {self.name}"


class Section(models.Model):
    branch = models.ForeignKey(
        Branch,
        on_delete=models.CASCADE,
        related_name='sections'
    )

    name = models.CharField(max_length=50)

    class Meta:
        unique_together = ('branch', 'name')

    def __str__(self):
        return f"{self.branch.name} - Section {self.name}"


class Semester(models.Model):
    class Status(models.TextChoices):
        DRAFT = 'DRAFT', 'Draft'
        ACTIVE = 'ACTIVE', 'Active'
        ARCHIVED = 'ARCHIVED', 'Archived'

    department = models.ForeignKey(
        Department,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    section = models.ForeignKey(
        Section,
        on_delete=models.CASCADE,
        related_name='semesters',
        null=True
    )

    semester_number = models.IntegerField()

    start_date = models.DateField()

    end_date = models.DateField()

    is_active = models.BooleanField(
        default=True
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.ACTIVE
    )

    def save(self, *args, **kwargs):
        if self.section:
            self.department = self.section.branch.department
        super().save(*args, **kwargs)

    def __str__(self):
        prefix = f"{self.section} - " if self.section else ""
        return f"{prefix}Semester {self.semester_number}"


class Subject(models.Model):

    semester = models.ForeignKey(
        Semester,
        on_delete=models.CASCADE
    )

    name = models.CharField(
        max_length=150
    )

    code = models.CharField(
        max_length=20
    )

    credits = models.IntegerField(
        default=3
    )

    def __str__(self):
        return self.name


class SubjectCatalog(models.Model):
    name = models.CharField(max_length=150)
    code = models.CharField(max_length=20, unique=True)
    description = models.TextField(blank=True)
    credits = models.IntegerField(default=3)
    created_by = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.code} - {self.name}"


class SemesterSubject(models.Model):
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE, related_name='semester_subjects')
    subject_catalog = models.ForeignKey(SubjectCatalog, on_delete=models.CASCADE, related_name='semester_subjects')
    assigned_by = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True, blank=True)
    assigned_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('semester', 'subject_catalog')

    def __str__(self):
        return f"{self.subject_catalog.name} in {self.semester}"


class SubjectUnit(models.Model):
    subject_catalog = models.ForeignKey(SubjectCatalog, on_delete=models.CASCADE, related_name='units')
    unit_number = models.IntegerField()
    title = models.CharField(max_length=150)
    description = models.TextField(blank=True)

    class Meta:
        unique_together = ('subject_catalog', 'unit_number')

    def __str__(self):
        return f"{self.subject_catalog.code} Unit {self.unit_number}: {self.title}"


class SubjectTopic(models.Model):
    subject_unit = models.ForeignKey(SubjectUnit, on_delete=models.CASCADE, related_name='topics')
    title = models.CharField(max_length=150)
    description = models.TextField(blank=True)
    estimated_hours = models.IntegerField(default=1)

    def __str__(self):
        return f"{self.subject_unit.subject_catalog.code} Topic: {self.title}"


class DailyClassReview(models.Model):
    semester_subject = models.ForeignKey(SemesterSubject, on_delete=models.CASCADE, related_name='daily_reviews')
    cr_assignment = models.ForeignKey('accounts.CRAssignment', on_delete=models.CASCADE, related_name='daily_reviews')
    title = models.CharField(max_length=200)
    class_date = models.DateField()
    timetable_entry = models.ForeignKey('TimetableEntry', on_delete=models.SET_NULL, null=True, blank=True, related_name='daily_reviews')
    
    # New V3 topics mapping (Source of Truth)
    topics = models.ManyToManyField(SubjectTopic, related_name='daily_reviews', blank=True)
    
    # Legacy fallback field
    topics_covered = models.TextField()
    faculty_notes = models.TextField(blank=True)
    important_questions = models.TextField(blank=True)
    exam_hints = models.TextField(blank=True)
    resources = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.class_date} - {self.title} ({self.semester_subject.subject_catalog.name})"


class SemesterKnowledgeBase(models.Model):
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE, related_name='knowledge_base')
    subject = models.ForeignKey(SemesterSubject, on_delete=models.CASCADE, related_name='knowledge_base')
    daily_review = models.OneToOneField(DailyClassReview, on_delete=models.CASCADE, related_name='knowledge_entry')
    extracted_topics = models.JSONField(default=list)
    summary = models.TextField()
    embedding_reference = models.UUIDField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Memory for {self.subject.subject_catalog.name} on {self.daily_review.class_date}"


class FacultyAssignment(models.Model):
    faculty = models.ForeignKey('accounts.Faculty', on_delete=models.CASCADE, related_name='assignments')
    semester_subject = models.ForeignKey(SemesterSubject, on_delete=models.CASCADE, related_name='faculty_assignments')
    assigned_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('faculty', 'semester_subject')

    def __str__(self):
        return f"{self.faculty.name} assigned to {self.semester_subject}"


class SemesterCalendar(models.Model):
    class EventType(models.TextChoices):
        WORKING_DAY = 'WORKING_DAY', 'Working Day'
        HOLIDAY = 'HOLIDAY', 'Holiday'
        INTERNAL_EXAM = 'INTERNAL_EXAM', 'Internal Exam'
        EXTERNAL_EXAM = 'EXTERNAL_EXAM', 'External Exam'
        EVENT = 'EVENT', 'Event'

    semester = models.ForeignKey(Semester, on_delete=models.CASCADE, related_name='calendars')
    event_type = models.CharField(max_length=50, choices=EventType.choices)
    title = models.CharField(max_length=150)
    event_date = models.DateField()

    def __str__(self):
        return f"{self.event_date} - {self.title} ({self.semester})"


class SemesterPlan(models.Model):
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE, related_name='plans')
    generated_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"AI Plan for {self.semester} generated at {self.generated_at}"


class SemesterPlanDay(models.Model):
    semester_plan = models.ForeignKey(SemesterPlan, on_delete=models.CASCADE, related_name='days')
    day_number = models.IntegerField()
    date = models.DateField()
    working_day = models.BooleanField(default=True)
    holiday = models.BooleanField(default=False)
    planned_subjects = models.ManyToManyField(SemesterSubject, blank=True)
    planned_topics = models.ManyToManyField(SubjectTopic, blank=True)
    planned_faculty = models.ManyToManyField('accounts.Faculty', blank=True)
    remarks = models.TextField(blank=True)

    def __str__(self):
        return f"Day {self.day_number} - {self.date} Plan"


class TopicProgress(models.Model):
    semester_subject = models.ForeignKey(SemesterSubject, on_delete=models.CASCADE, related_name='topic_progress')
    subject_topic = models.ForeignKey(SubjectTopic, on_delete=models.CASCADE, related_name='progress_records')
    completion_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    last_reviewed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ('semester_subject', 'subject_topic')

    def __str__(self):
        return f"{self.subject_topic.title} - {self.completion_percentage}%"


class SectionSemester(models.Model):
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE, related_name='section_semesters')
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, related_name='section_semesters')
    section = models.ForeignKey(Section, on_delete=models.CASCADE, related_name='section_semesters')
    start_date = models.DateField()
    end_date = models.DateField()
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ('semester', 'branch', 'section')

    def __str__(self):
        return f"{self.branch.code} - {self.section.name} - Sem {self.semester.semester_number}"


class Timetable(models.Model):
    section_semester = models.ForeignKey(SectionSemester, on_delete=models.CASCADE, related_name='timetables')
    timetable_pdf = models.ForeignKey('resources.StoredFile', on_delete=models.CASCADE, related_name='timetables')
    uploaded_by = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Timetable for {self.section_semester}"


class TimetableEntry(models.Model):
    class DayOfWeek(models.TextChoices):
        MONDAY = 'MONDAY', 'Monday'
        TUESDAY = 'TUESDAY', 'Tuesday'
        WEDNESDAY = 'WEDNESDAY', 'Wednesday'
        THURSDAY = 'THURSDAY', 'Thursday'
        FRIDAY = 'FRIDAY', 'Friday'
        SATURDAY = 'SATURDAY', 'Saturday'
        SUNDAY = 'SUNDAY', 'Sunday'

    timetable = models.ForeignKey(Timetable, on_delete=models.CASCADE, related_name='entries')
    day_of_week = models.CharField(max_length=15, choices=DayOfWeek.choices)
    period_number = models.IntegerField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    subject = models.ForeignKey(SemesterSubject, on_delete=models.CASCADE, related_name='timetable_entries')
    faculty = models.ForeignKey('accounts.Faculty', on_delete=models.CASCADE, related_name='timetable_entries')
    room = models.CharField(max_length=50)

    class Meta:
        unique_together = ('timetable', 'day_of_week', 'period_number')

    def __str__(self):
        return f"{self.timetable.section_semester} - {self.day_of_week} P{self.period_number} ({self.subject.subject_catalog.name})"


class Attendance(models.Model):
    student = models.ForeignKey('accounts.Student', on_delete=models.CASCADE, related_name='attendances')
    timetable_entry = models.ForeignKey(TimetableEntry, on_delete=models.CASCADE, related_name='attendances')
    date = models.DateField()
    status = models.CharField(
        max_length=20,
        choices=[('PRESENT', 'Present'), ('ABSENT', 'Absent'), ('LATE', 'Late')]
    )
    marked_by = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True, blank=True)
    marked_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('student', 'timetable_entry', 'date')

    def __str__(self):
        return f"{self.student.name} - {self.timetable_entry.subject.subject_catalog.name} ({self.date}): {self.status}"



