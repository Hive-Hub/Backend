from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Student, CR, CRAssignment, SemesterEnrollment, JoinSemesterRequest, SubjectProgress, SemesterProgress, SemesterReport, Faculty

# Custom User Admin to display the new role field
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ('Custom Fields', {'fields': ('role',)}),
    )
    list_display = ('username', 'email', 'first_name', 'last_name', 'role', 'is_staff')

admin.site.register(User, CustomUserAdmin)
admin.site.register(Student)
admin.site.register(CR)
admin.site.register(CRAssignment)
admin.site.register(SemesterEnrollment)
admin.site.register(JoinSemesterRequest)
admin.site.register(SubjectProgress)
admin.site.register(SemesterProgress)
admin.site.register(SemesterReport)
admin.site.register(Faculty)



