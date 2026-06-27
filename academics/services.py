import json
import datetime
from django.utils import timezone
from django.core.files.storage import default_storage
import urllib.request
from django.db import transaction

from academics.models import SemesterSubject, TimetableEntry, SectionSemester
from accounts.models import Faculty
from config.ai_utils import extract_timetable_pdf, get_gemini_client

def get_stored_file_bytes(stored_file):
    """
    Retrieves file bytes from a StoredFile record.
    """
    # 1. Try reading via Django default storage
    try:
        if default_storage.exists(stored_file.file_name):
            with default_storage.open(stored_file.file_name) as f:
                return f.read()
    except Exception:
        pass

    # 2. Try HTTP download
    try:
        url = stored_file.file_url
        req = urllib.request.Request(
            url,
            headers={'User-Agent': 'Mozilla/5.0'}
        )
        with urllib.request.urlopen(req) as response:
            return response.read()
    except Exception as e:
        raise ValueError(f"Could not retrieve file bytes for {stored_file}: {e}")


def populate_timetable_from_pdf(timetable):
    """
    Extracts timetable details from PDF using Gemini and populates TimetableEntry records.
    """
    from django.conf import settings
    
    stored_file = timetable.timetable_pdf
    if not stored_file:
        return

    # Delete existing entries first
    timetable.entries.all().delete()

    # Get file bytes
    try:
        file_bytes = get_stored_file_bytes(stored_file)
    except Exception as e:
        # Fallback to simulated scheduling if file retrieval fails
        generate_simulated_timetable(timetable)
        return

    # Call Gemini API or use fallback
    data = None
    # If the file is just dummy text from the seeder, use simulated schedule immediately
    if len(file_bytes) < 500 or b"Timetable:" in file_bytes or b"ContentFile" in file_bytes:
        generate_simulated_timetable(timetable)
        return

    try:
        raw_result = extract_timetable_pdf(file_bytes, stored_file.file_name)
        data = json.loads(raw_result)
    except Exception:
        pass

    if not data or "entries" not in data or not data["entries"]:
        generate_simulated_timetable(timetable)
        return

    # Populate records
    semester = timetable.section_semester.semester
    semester_subjects = list(SemesterSubject.objects.filter(semester=semester))
    all_faculty = list(Faculty.objects.all())

    if not semester_subjects:
        return  # Cannot create entries without subjects

    with transaction.atomic():
        for entry_data in data["entries"]:
            # 1. Map Subject
            subj_code = entry_data.get("subject_code", "")
            subject = None
            for ss in semester_subjects:
                if (subj_code.lower() in ss.subject_catalog.code.lower() or 
                    subj_code.lower() in ss.subject_catalog.name.lower()):
                    subject = ss
                    break
            if not subject:
                # fallback
                subject = semester_subjects[0]

            # 2. Map Faculty
            fac_info = entry_data.get("faculty_email_or_name", "")
            faculty = None
            for fac in all_faculty:
                if (fac_info.lower() in fac.email.lower() or 
                    fac_info.lower() in fac.name.lower()):
                    faculty = fac
                    break
            if not faculty:
                # fallback
                faculty = all_faculty[0] if all_faculty else Faculty.objects.create(
                    name="Default Faculty",
                    email="default_faculty@qis.edu",
                    department=semester.department
                )

            # 3. Day of week clean
            day = entry_data.get("day_of_week", "MONDAY").upper().strip()
            valid_days = [d[0] for d in TimetableEntry.DayOfWeek.choices]
            if day not in valid_days:
                day = "MONDAY"

            # 4. Period & Times
            period = entry_data.get("period_number", 1)
            
            try:
                start_str = entry_data.get("start_time", "09:00")
                start_time = datetime.datetime.strptime(start_str, "%H:%M").time()
            except Exception:
                start_time = datetime.time(9, 0)

            try:
                end_str = entry_data.get("end_time", "10:00")
                end_time = datetime.datetime.strptime(end_str, "%H:%M").time()
            except Exception:
                end_time = datetime.time(10, 0)

            room = entry_data.get("room", "Room 301")

            TimetableEntry.objects.create(
                timetable=timetable,
                day_of_week=day,
                period_number=period,
                start_time=start_time,
                end_time=end_time,
                subject=subject,
                faculty=faculty,
                room=room
            )


def generate_simulated_timetable(timetable):
    """
    Generates a mock/simulated timetable schedule in case of API failure or local environment tests.
    """
    semester = timetable.section_semester.semester
    semester_subjects = list(SemesterSubject.objects.filter(semester=semester))
    all_faculty = list(Faculty.objects.all())

    if not semester_subjects:
        return

    # Use existing faculty or create a placeholder
    faculty = all_faculty[0] if all_faculty else Faculty.objects.create(
        name="Default Faculty",
        email="default_faculty@qis.edu",
        department=semester.department
    )

    days = ["MONDAY", "TUESDAY", "WEDNESDAY", "THURSDAY", "FRIDAY", "SATURDAY"]
    periods_times = [
        (1, "09:00", "09:50"),
        (2, "09:50", "10:40"),
        (3, "11:00", "11:50"),
        (4, "11:50", "12:40"),
        (5, "13:40", "14:30"),
        (6, "14:30", "15:20"),
    ]

    with transaction.atomic():
        for day in days:
            for p_num, start_str, end_str in periods_times:
                # Rotate through semester subjects
                subject = semester_subjects[(days.index(day) * 6 + p_num) % len(semester_subjects)]
                
                # Pick assigned faculty if available
                subj_fac = list(Faculty.objects.filter(assignments__semester_subject=subject))
                assigned_faculty = subj_fac[0] if subj_fac else faculty

                TimetableEntry.objects.create(
                    timetable=timetable,
                    day_of_week=day,
                    period_number=p_num,
                    start_time=datetime.datetime.strptime(start_str, "%H:%M").time(),
                    end_time=datetime.datetime.strptime(end_str, "%H:%M").time(),
                    subject=subject,
                    faculty=assigned_faculty,
                    room=f"Room {100 + semester.semester_number * 10 + p_num}"
                )


from academics.models import DailyClassReview, SubjectTopic, TopicProgress
from django.core.exceptions import ValidationError
from .validators import validate_review_topics
from accounts.models import Student, CR, CRAssignment, SubjectProgress

class AcademicsService:
    @staticmethod
    def create_daily_review(cr_user, data):
        """
        Creates a new Daily Class Review and tracks covered topics.
        """
        semester_subject_id = data.get('semester_subject')
        timetable_entry_id = data.get('timetable_entry')
        title = data.get('title')
        class_date = data.get('class_date')
        topic_ids = data.get('topics', [])
        topics_covered = data.get('topics_covered', '')
        faculty_notes = data.get('faculty_notes', '')
        important_questions = data.get('important_questions', '')
        exam_hints = data.get('exam_hints', '')
        resources = data.get('resources', '')

        try:
            student = Student.objects.get(user=cr_user)
            cr_assignment = CRAssignment.objects.get(student=student, is_active=True)
        except (Student.DoesNotExist, CRAssignment.DoesNotExist):
            raise ValidationError("User is not an active CR.")

        try:
            semester_subject = SemesterSubject.objects.get(id=semester_subject_id)
        except SemesterSubject.DoesNotExist:
            raise ValidationError("Invalid Semester Subject.")

        topics = SubjectTopic.objects.filter(id__in=topic_ids)
        validate_review_topics(semester_subject, topics)

        review = DailyClassReview.objects.create(
            semester_subject=semester_subject,
            cr_assignment=cr_assignment,
            title=title,
            class_date=class_date,
            timetable_entry_id=timetable_entry_id,
            topics_covered=topics_covered,
            faculty_notes=faculty_notes,
            important_questions=important_questions,
            exam_hints=exam_hints,
            resources=resources
        )
        if topic_ids:
            review.topics.set(topics)
            
            # Increment progress for the selected topics
            for topic in topics:
                prog, _ = TopicProgress.objects.get_or_create(
                    semester_subject=semester_subject,
                    subject_topic=topic
                )
                prog.completion_percentage = 100.0
                prog.last_reviewed_at = timezone.now()
                prog.save()

            # Recalculate overall SubjectProgress for students in the section
            students = Student.objects.filter(semester=semester_subject.semester)
            total_topics = SubjectTopic.objects.filter(subject_unit__subject_catalog=semester_subject.subject_catalog).count()
            
            if total_topics > 0:
                completed = TopicProgress.objects.filter(semester_subject=semester_subject, completion_percentage__gte=100.0).count()
                completion_pct = (completed / total_topics) * 100.0
                
                for s in students:
                    subj_progress, _ = SubjectProgress.objects.get_or_create(
                        student=s,
                        semester_subject=semester_subject
                    )
                    subj_progress.completion_percentage = completion_pct
                    subj_progress.save()

        return review
