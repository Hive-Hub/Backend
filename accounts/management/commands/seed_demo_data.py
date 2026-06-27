import random
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from colleges.models import College
from academics.models import (
    Department, Branch, Section, Semester, Subject, SubjectCatalog, SemesterSubject,
    DailyClassReview, SemesterKnowledgeBase, SubjectUnit, SubjectTopic,
    FacultyAssignment, SemesterCalendar, SemesterPlan, SemesterPlanDay, TopicProgress,
    SectionSemester, Timetable, TimetableEntry, Attendance
)
from accounts.models import (
    Student, CR, CRAssignment, SemesterEnrollment, JoinSemesterRequest,
    SubjectProgress, SemesterProgress, SemesterReport, Faculty
)
from assignments.models import Assignment, QuestionBank, AssignmentSubmission
from announcements.models import Announcement
from resources.models import Resource, StoredFile, ResourceLibrary

User = get_user_model()


class Command(BaseCommand):
    help = "Seeds database with mock data for QISHub V3 AI Academic OS transformation"

    def handle(self, *args, **options):
        self.stdout.write("Purging existing data...")
        
        # Purge reverse dependency order
        Attendance.objects.all().delete()
        TimetableEntry.objects.all().delete()
        Timetable.objects.all().delete()
        AssignmentSubmission.objects.all().delete()
        QuestionBank.objects.all().delete()
        Assignment.objects.all().delete()
        Announcement.objects.all().delete()
        ResourceLibrary.objects.all().delete()
        Resource.objects.all().delete()
        StoredFile.objects.all().delete()
        SemesterKnowledgeBase.objects.all().delete()
        DailyClassReview.objects.all().delete()
        TopicProgress.objects.all().delete()
        SemesterPlanDay.objects.all().delete()
        SemesterPlan.objects.all().delete()
        SemesterCalendar.objects.all().delete()
        FacultyAssignment.objects.all().delete()
        Faculty.objects.all().delete()
        SubjectProgress.objects.all().delete()
        SemesterProgress.objects.all().delete()
        SemesterReport.objects.all().delete()
        CRAssignment.objects.all().delete()
        CR.objects.all().delete()
        SemesterEnrollment.objects.all().delete()
        JoinSemesterRequest.objects.all().delete()
        Student.objects.all().delete()
        User.objects.filter(is_superuser=False).delete()
        
        SectionSemester.objects.all().delete()
        SemesterSubject.objects.all().delete()
        SubjectCatalog.objects.all().delete()
        Subject.objects.all().delete()
        Semester.objects.all().delete()
        Section.objects.all().delete()
        Branch.objects.all().delete()
        Department.objects.all().delete()
        College.objects.all().delete()

        self.stdout.write("Seeding academic structure...")

        # 1. College
        college = College.objects.create(name="QIS College", code="QIS")

        # 2. Departments
        cse = Department.objects.create(college=college, name="CSE", code="CSE")
        ece = Department.objects.create(college=college, name="ECE", code="ECE")

        # 3. Branches
        ds = Branch.objects.create(department=cse, name="Data Science", code="CSE-DS")
        aiml = Branch.objects.create(department=cse, name="AI & ML", code="CSE-AIML")
        ece_comm = Branch.objects.create(department=ece, name="Communications Engineering", code="ECE-COMM")
        ece_vlsi = Branch.objects.create(department=ece, name="VLSI Design", code="ECE-VLSI")
        branches = [ds, aiml, ece_comm, ece_vlsi]

        # 4. Sections
        sections = []
        for branch in branches:
            sections.append(Section.objects.create(branch=branch, name="Section A"))
            sections.append(Section.objects.create(branch=branch, name="Section B"))

        # 5. Semesters
        semesters = []
        start_date = timezone.now().date() - timezone.timedelta(days=30)
        end_date = start_date + timezone.timedelta(days=120)
        for section in sections:
            for sem_num in [1, 2, 3, 4]:
                semesters.append(
                    Semester.objects.create(
                        section=section,
                        semester_number=sem_num,
                        start_date=start_date,
                        end_date=end_date,
                        status=Semester.Status.ACTIVE
                    )
                )

        # 5b. Section semesters
        self.stdout.write("Seeding SectionSemesters...")
        section_semesters = []
        for sem in semesters:
            section_semesters.append(
                SectionSemester.objects.create(
                    semester=sem,
                    branch=sem.section.branch,
                    section=sem.section,
                    start_date=sem.start_date,
                    end_date=sem.end_date,
                    is_active=True
                )
            )

        # 6. Faculty Seeding (20 Members)
        self.stdout.write("Seeding faculty members...")
        faculty_list = []
        designations = ["Professor", "Assistant Professor", "Associate Professor"]
        for idx in range(1, 21):
            faculty_list.append(
                Faculty.objects.create(
                    name=f"Faculty Name {idx}",
                    email=f"faculty{idx}@qis.edu",
                    phone=f"98765432{idx:02d}",
                    designation=random.choice(designations),
                    department=random.choice([cse, ece])
                )
            )

        # 7. Subject Catalog (10 Subjects)
        self.stdout.write("Seeding Subject Catalog...")
        catalogs = [
            SubjectCatalog.objects.create(name="Database Management Systems", code="CS301", credits=3),
            SubjectCatalog.objects.create(name="Java Programming", code="CS302", credits=4),
            SubjectCatalog.objects.create(name="Probability & Statistics", code="BS301", credits=3),
            SubjectCatalog.objects.create(name="Operating Systems", code="CS303", credits=4),
            SubjectCatalog.objects.create(name="Computer Networks", code="CS304", credits=3),
            SubjectCatalog.objects.create(name="Compiler Design", code="CS305", credits=4),
            SubjectCatalog.objects.create(name="Software Engineering", code="CS306", credits=3),
            SubjectCatalog.objects.create(name="Machine Learning", code="CS307", credits=4),
            SubjectCatalog.objects.create(name="Deep Learning", code="CS308", credits=4),
            SubjectCatalog.objects.create(name="Discrete Mathematics", code="BS302", credits=3),
        ]

        # 8. Units (50 Units - 5 per subject catalog)
        self.stdout.write("Seeding units...")
        units = []
        for cat in catalogs:
            for u_num in range(1, 6):
                units.append(
                    SubjectUnit(
                        subject_catalog=cat,
                        unit_number=u_num,
                        title=f"Unit {u_num}: Core Foundations",
                        description=f"Overview of unit {u_num} for {cat.name}"
                    )
                )
        SubjectUnit.objects.bulk_create(units)
        units = list(SubjectUnit.objects.all())

        # 9. Topics (300 Topics - 6 per unit)
        self.stdout.write("Seeding topics...")
        topics = []
        for unit in units:
            for t_num in range(1, 7):
                topics.append(
                    SubjectTopic(
                        subject_unit=unit,
                        title=f"Topic {t_num}: Detail Syllabus Segment",
                        description=f"Topics include details on standard syllabus specs.",
                        estimated_hours=2
                    )
                )
        SubjectTopic.objects.bulk_create(topics)
        topics = list(SubjectTopic.objects.all())

        # Map Subject Catalog to semesters (Creating SemesterSubjects)
        semester_subjects = []
        for sem in semesters:
            # Assign 4 subjects to each semester
            assigned_catalogs = random.sample(catalogs, k=4)
            for cat in assigned_catalogs:
                semester_subjects.append(
                    SemesterSubject.objects.create(
                        semester=sem,
                        subject_catalog=cat
                    )
                )

        # Seeding Faculty Assignments
        faculty_assignments = []
        for ss in semester_subjects:
            assigned_fac = random.sample(faculty_list, k=random.randint(1, 2))
            for fac in assigned_fac:
                faculty_assignments.append(
                    FacultyAssignment.objects.create(
                        faculty=fac,
                        semester_subject=ss
                    )
                )

        # 10. Seed Users & Students (100 Students)
        self.stdout.write("Seeding users and students...")
        students = []
        for i in range(1, 101):
            user = User.objects.create_user(
                username=f"student{i:03d}",
                email=f"student{i:03d}@qis.edu",
                password="password123",
                role=User.Role.STUDENT
            )
            
            # Select random branch, section, and semester
            assigned_branch = random.choice(branches)
            assigned_section = random.choice([s for s in sections if s.branch == assigned_branch])
            assigned_semester = random.choice([sem for sem in semesters if sem.section == assigned_section])

            student = Student.objects.create(
                user=user,
                register_number=f"QIS{i:05d}",
                name=f"Student {i}",
                email=user.email,
                phone=f"98765432{i:02d}",
                college=college,
                department=assigned_branch.department,
                branch=assigned_branch,
                section=assigned_section,
                semester=assigned_semester
            )
            students.append(student)

            # Create SemesterEnrollment for active semester
            SemesterEnrollment.objects.create(
                student=student,
                semester=assigned_semester,
                is_active=True
            )

        # 11. Seed 10 CR Assignments
        self.stdout.write("Seeding CR assignments...")
        crs = []
        cr_semesters = random.sample(semesters, k=8) + random.sample(semesters, k=2) # 10 CR slots
        for sem in cr_semesters:
            students_in_sem = [s for s in students if s.semester == sem]
            if not students_in_sem:
                s = random.choice(students)
                s.semester = sem
                s.section = sem.section
                s.branch = sem.section.branch
                s.department = sem.section.branch.department
                s.save()
                students_in_sem = [s]
            
            cr_student = random.choice(students_in_sem)
            cr_assignment, _ = CRAssignment.objects.get_or_create(
                student=cr_student,
                semester=sem,
                defaults={
                    "branch": sem.section.branch,
                    "section": sem.section,
                    "is_active": True
                }
            )
            crs.append(cr_assignment)

        # 12. Upload dummy files to Supabase S3 bucket
        self.stdout.write("Uploading files to Supabase...")
        demo_files = [
            "notes/timetable.pdf",
            "notes/calendar.pdf",
            "notes/dbms-notes.pdf",
            "notes/java-notes.pdf",
            "notes/previous-papers.pdf"
        ]
        for f in demo_files:
            if default_storage.exists(f):
                default_storage.delete(f)
                
        default_storage.save("notes/timetable.pdf", ContentFile("Timetable: Daily class and period details."))
        default_storage.save("notes/calendar.pdf", ContentFile("Academic Calendar: Exams and holiday list."))
        default_storage.save("notes/dbms-notes.pdf", ContentFile("DBMS Notes: Normalized forms and relational logic."))
        default_storage.save("notes/java-notes.pdf", ContentFile("Java Notes: Multithreading and oops."))
        default_storage.save("notes/previous-papers.pdf", ContentFile("Previous Paper: Midterm question sheets."))

        # Create StoredFile records
        stored_files = []
        for f in demo_files:
            stored_files.append(
                StoredFile.objects.create(
                    file_name=f.split("/")[-1],
                    file_url=default_storage.url(f),
                    bucket_name="StudentHub",
                    mime_type="application/pdf",
                    size=1024,
                    version=1
                )
            )

        # 12b. Seed Timetables & Entries (triggers generate_simulated_timetable)
        self.stdout.write("Seeding Timetables & Entries...")
        timetable_pdf = stored_files[0] # notes/timetable.pdf
        for sec_sem in section_semesters:
            Timetable.objects.create(
                section_semester=sec_sem,
                timetable_pdf=timetable_pdf
            )

        # 12c. Seed student attendance check-ins
        self.stdout.write("Seeding student attendance check-ins...")
        attendances = []
        today = timezone.now().date()
        for student in students:
            # Let's mock attendance for the last 3 days
            for offset in range(3):
                date = today - timezone.timedelta(days=offset)
                if date.weekday() == 6:  # Skip Sunday
                    continue
                
                schedule = student.get_daily_schedule(date)
                for entry in schedule:
                    attendances.append(
                        Attendance(
                            student=student,
                            timetable_entry=entry,
                            date=date,
                            status=random.choice(['PRESENT', 'PRESENT', 'PRESENT', 'ABSENT', 'LATE']),
                            marked_at=timezone.now()
                        )
                    )
        Attendance.objects.bulk_create(attendances)

        # 13. Seeding 300 Resources (StoredFile + ResourceLibrary + Legacy Resource)
        self.stdout.write("Seeding 300 resources...")
        resource_libraries = []
        legacy_resources = []
        
        types_pool = [
            ResourceLibrary.ResourceType.NOTES, ResourceLibrary.ResourceType.PPT,
            ResourceLibrary.ResourceType.QUESTION_BANK, ResourceLibrary.ResourceType.PREVIOUS_PAPER,
            ResourceLibrary.ResourceType.SYLLABUS, ResourceLibrary.ResourceType.LAB_MANUAL
        ]

        for r_idx in range(1, 301):
            ss = random.choice(semester_subjects)
            cr = random.choice(crs)
            st_file = random.choice(stored_files)
            
            # 1. Resource Library
            resource_libraries.append(
                ResourceLibrary(
                    semester=ss.semester,
                    subject=ss,
                    file=st_file,
                    resource_type=random.choice(types_pool)
                )
            )

            # 2. Legacy Resource
            legacy_sub = Subject.objects.filter(semester=ss.semester, code=ss.subject_catalog.code).first()
            legacy_resources.append(
                Resource(
                    title=f"Study Resource {r_idx} - {ss.subject_catalog.name}",
                    description="Standard study notes description.",
                    file_url=st_file.file_url,
                    subject=legacy_sub,
                    uploaded_by=CR.objects.get_or_create(student=cr.student)[0]
                )
            )
            
        ResourceLibrary.objects.bulk_create(resource_libraries)
        Resource.objects.bulk_create(legacy_resources)

        # 14. Seeding 100 Daily Class Reviews with topics
        self.stdout.write("Seeding daily class reviews...")
        reviews = []
        for rev_idx in range(1, 101):
            cr = random.choice(crs)
            sem_subs = [ss for ss in semester_subjects if ss.semester == cr.semester]
            if not sem_subs:
                continue
            ss = random.choice(sem_subs)
            review = DailyClassReview.objects.create(
                semester_subject=ss,
                cr_assignment=cr,
                title=f"Review Topic {rev_idx} - {ss.subject_catalog.name}",
                class_date=timezone.now().date() - timezone.timedelta(days=random.randint(0, 30)),
                topics_covered="Coverage details logged in text.",
                faculty_notes="Keep revising normal forms as it carries high weightage.",
                resources=random.choice(stored_files).file_url
            )
            
            # Link to TimetableEntry matching weekday, subject and CR section
            day_name = review.class_date.strftime('%A').upper()
            entry = TimetableEntry.objects.filter(
                timetable__section_semester__semester=ss.semester,
                timetable__section_semester__branch=cr.branch,
                timetable__section_semester__section=cr.section,
                subject=ss,
                day_of_week=day_name
            ).first()
            if entry:
                review.timetable_entry = entry
                review.save(update_fields=['timetable_entry'])

            # Map random topics to the review
            sub_topics = [t for t in topics if t.subject_unit.subject_catalog_id == ss.subject_catalog_id]
            if sub_topics:
                review.topics.add(*random.sample(sub_topics, k=min(len(sub_topics), random.randint(1, 3))))
            
            # Automatically populate progress trackers
            for topic in review.topics.all():
                TopicProgress.objects.get_or_create(
                    semester_subject=ss,
                    subject_topic=topic,
                    defaults={"completion_percentage": 100.00, "last_reviewed_at": timezone.now()}
                )

        # 15. Seeding 100 Assignments
        self.stdout.write("Seeding 100 assignments...")
        for k in range(60):
            cr = random.choice(crs)
            sem_subs = [ss for ss in semester_subjects if ss.semester == cr.semester]
            if not sem_subs:
                continue
            ss = random.choice(sem_subs)
            legacy_sub = Subject.objects.filter(semester=cr.semester, code=ss.subject_catalog.code).first()

            Assignment.objects.create(
                title=f"Timetable Quiz {k+1} - {ss.subject_catalog.name}",
                description="Outline answer sheets cleanly.",
                deadline=timezone.now() + timezone.timedelta(days=7),
                subject=legacy_sub,
                semester_subject=ss,
                created_by=CR.objects.get_or_create(student=cr.student)[0],
                assignment_type=Assignment.AssignmentType.COLLEGE,
                start_date=timezone.now(),
                end_date=timezone.now() + timezone.timedelta(days=7),
                external_link=random.choice(stored_files).file_url
            )

        for k in range(40):
            ss = random.choice(semester_subjects)
            legacy_sub = Subject.objects.filter(semester=ss.semester, code=ss.subject_catalog.code).first()

            Assignment.objects.create(
                title=f"AI Generated Test {k+1}",
                description="Interactive AI assignment covering topic normalizations.",
                deadline=timezone.now() + timezone.timedelta(days=2),
                subject=legacy_sub,
                semester_subject=ss,
                assignment_type=Assignment.AssignmentType.AI_GENERATED,
                difficulty=Assignment.Difficulty.MEDIUM,
                topic="Transactions & Locking Protocols",
                generated_questions=[
                    {"question": "Explain ACID Properties.", "type": "SHORT", "answer": "Atomicity, Consistency, Isolation, Durability"}
                ]
            )

        # 16. Seeding 100 QuestionBank records
        self.stdout.write("Seeding QuestionBank...")
        for q_idx in range(1, 101):
            ss = random.choice(semester_subjects)
            sub_topics = [t for t in topics if t.subject_unit.subject_catalog_id == ss.subject_catalog_id]
            if not sub_topics:
                continue
            topic = random.choice(sub_topics)
            QuestionBank.objects.create(
                subject=ss,
                topic=topic.title,
                question_type=QuestionBank.QuestionType.MCQ,
                difficulty=QuestionBank.Difficulty.MEDIUM,
                question=f"Sample Question {q_idx}?",
                answer="Option A"
            )

        # 17. Seeding 10 Semester Plans and 1400 plan day entries
        self.stdout.write("Seeding 10 semester plans and 1400 roadmap days...")
        # Create SemesterPlans
        plans = []
        target_sems = semesters[:10]
        for sem in target_sems:
            plans.append(SemesterPlan(semester=sem))
        SemesterPlan.objects.bulk_create(plans)
        plans = list(SemesterPlan.objects.all())

        # Bulk create SemesterPlanDays
        plan_days = []
        for plan in plans:
            curr_date = plan.semester.start_date
            for d in range(1, 141):
                plan_days.append(
                    SemesterPlanDay(
                        semester_plan=plan,
                        day_number=d,
                        date=curr_date,
                        working_day=(curr_date.weekday() < 5),
                        holiday=(curr_date.weekday() == 6),
                        remarks=f"Roadmap syllabus schedule for day {d}."
                    )
                )
                curr_date += timezone.timedelta(days=1)
        
        SemesterPlanDay.objects.bulk_create(plan_days)
        plan_days = list(SemesterPlanDay.objects.all())

        # Link plan day subjects, topics, and faculty assignments in bulk
        PlannedSubjectJunction = SemesterPlanDay.planned_subjects.through
        PlannedTopicJunction = SemesterPlanDay.planned_topics.through
        PlannedFacultyJunction = SemesterPlanDay.planned_faculty.through

        sub_juncs = []
        top_juncs = []
        fac_juncs = []

        for day in plan_days:
            sem_subs = [ss for ss in semester_subjects if ss.semester == day.semester_plan.semester]
            if sem_subs:
                ss = random.choice(sem_subs)
                sub_juncs.append(PlannedSubjectJunction(semesterplanday_id=day.id, semestersubject_id=ss.id))
                
                # Fetch topics of this subject
                sub_topics = [t for t in topics if t.subject_unit.subject_catalog_id == ss.subject_catalog_id]
                if sub_topics:
                    top_juncs.append(PlannedTopicJunction(semesterplanday_id=day.id, subjecttopic_id=random.choice(sub_topics).id))
                
                # Fetch faculty assigned
                fac_assign = [fa.faculty_id for fa in faculty_assignments if fa.semester_subject_id == ss.id]
                if fac_assign:
                    fac_juncs.append(PlannedFacultyJunction(semesterplanday_id=day.id, faculty_id=random.choice(fac_assign)))

        PlannedSubjectJunction.objects.bulk_create(sub_juncs)
        PlannedTopicJunction.objects.bulk_create(top_juncs)
        PlannedFacultyJunction.objects.bulk_create(fac_juncs)

        self.stdout.write(self.style.SUCCESS("V3 Database seeding completed successfully!"))
