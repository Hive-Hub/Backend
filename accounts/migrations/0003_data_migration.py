from django.db import migrations


def migrate_legacy_data(apps, schema_editor):
    Department = apps.get_model('academics', 'Department')
    Branch = apps.get_model('academics', 'Branch')
    Section = apps.get_model('academics', 'Section')
    Semester = apps.get_model('academics', 'Semester')
    Student = apps.get_model('accounts', 'Student')
    CR = apps.get_model('accounts', 'CR')
    CRAssignment = apps.get_model('accounts', 'CRAssignment')
    SemesterEnrollment = apps.get_model('accounts', 'SemesterEnrollment')
    Announcement = apps.get_model('announcements', 'Announcement')

    # Iterate through all departments
    for dept in Department.objects.all():
        # Get or create a default branch for the department
        branch, _ = Branch.objects.get_or_create(
            department=dept,
            name="General",
            defaults={"code": f"{dept.code}-GEN"}
        )
        
        # Get or create a default section for the branch
        section, _ = Section.objects.get_or_create(
            branch=branch,
            name="Section A"
        )

        # Map all legacy semesters to the new default Section
        semesters = Semester.objects.filter(department=dept)
        for sem in semesters:
            sem.section = section
            sem.save()

        # Update existing students' branch and section fields
        students = Student.objects.filter(department=dept)
        for student in students:
            student.branch = branch
            student.section = section
            student.save()

            # Create an active SemesterEnrollment for the student's current semester
            if student.semester:
                SemesterEnrollment.objects.get_or_create(
                    student=student,
                    semester=student.semester,
                    defaults={"is_active": True}
                )

    # Convert CR profiles into CRAssignment records
    for cr in CR.objects.all():
        student = cr.student
        if student.semester:
            CRAssignment.objects.get_or_create(
                student=student,
                semester=student.semester,
                branch=student.branch,
                section=student.section,
                defaults={
                    "is_active": cr.is_active,
                    "assigned_date": cr.assigned_at
                }
            )

    # Map existing announcements to the CR's current semester
    for ann in Announcement.objects.all():
        cr_student = ann.created_by.student
        if cr_student.semester:
            ann.semester = cr_student.semester
            ann.save()


class Migration(migrations.Migration):
    dependencies = [
        ('accounts', '0002_student_branch_student_section_and_more'),
        ('academics', '0002_semester_status_alter_semester_department_branch_and_more'),
        ('announcements', '0002_announcement_semester'),
    ]

    operations = [
        migrations.RunPython(migrate_legacy_data, reverse_code=migrations.RunPython.noop),
    ]
