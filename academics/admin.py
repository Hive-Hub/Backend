from django.contrib import admin
from .models import (
    Department, Branch, Section, Semester, Subject, SubjectCatalog, SemesterSubject,
    DailyClassReview, SemesterKnowledgeBase, SubjectUnit, SubjectTopic,
    FacultyAssignment, SemesterCalendar, SemesterPlan, SemesterPlanDay, TopicProgress,
    SectionSemester, Timetable, TimetableEntry, Attendance
)

admin.site.register(Department)
admin.site.register(Branch)
admin.site.register(Section)
admin.site.register(Semester)
admin.site.register(Subject)
admin.site.register(SubjectCatalog)
admin.site.register(SemesterSubject)
admin.site.register(DailyClassReview)
admin.site.register(SemesterKnowledgeBase)
admin.site.register(SubjectUnit)
admin.site.register(SubjectTopic)
admin.site.register(FacultyAssignment)
admin.site.register(SemesterCalendar)
admin.site.register(SemesterPlan)
admin.site.register(SemesterPlanDay)
admin.site.register(TopicProgress)
admin.site.register(SectionSemester)
admin.site.register(Timetable)
admin.site.register(TimetableEntry)
admin.site.register(Attendance)




