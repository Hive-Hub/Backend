from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import (
    Student, CR, CRAssignment, SemesterEnrollment, 
    JoinSemesterRequest, SubjectProgress, SemesterProgress, SemesterReport, Faculty
)
from colleges.models import College
from academics.models import Department, Semester, Branch, Section
from .validators import validate_phone_number

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'role']
        read_only_fields = ['id']


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)


class StudentProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    college_name = serializers.ReadOnlyField(source='college.name')
    department_name = serializers.ReadOnlyField(source='department.name')
    branch_name = serializers.ReadOnlyField(source='branch.name')
    section_name = serializers.ReadOnlyField(source='section.name')
    semester_number = serializers.ReadOnlyField(source='semester.semester_number')
    phone = serializers.CharField(validators=[validate_phone_number], required=False)

    class Meta:
        model = Student
        fields = [
            'id', 'user', 'register_number', 'name', 'email', 'phone', 
            'college', 'college_name', 'department', 'department_name', 
            'branch', 'branch_name', 'section', 'section_name', 
            'semester', 'semester_number', 'created_at'
        ]
        read_only_fields = ['id', 'register_number', 'college', 'department', 'branch', 'section', 'semester', 'created_at']


class CRSerializer(serializers.ModelSerializer):
    student_name = serializers.ReadOnlyField(source='student.name')
    email = serializers.ReadOnlyField(source='student.email')

    class Meta:
        model = CR
        fields = ['id', 'student', 'student_name', 'email', 'assigned_at', 'is_active']


class CRAssignmentSerializer(serializers.ModelSerializer):
    student_name = serializers.ReadOnlyField(source='student.name')
    semester_number = serializers.ReadOnlyField(source='semester.semester_number')
    section_name = serializers.ReadOnlyField(source='section.name')

    class Meta:
        model = CRAssignment
        fields = ['id', 'student', 'student_name', 'semester', 'semester_number', 'branch', 'section', 'section_name', 'is_active']


class SemesterEnrollmentSerializer(serializers.ModelSerializer):
    semester_number = serializers.ReadOnlyField(source='semester.semester_number')
    
    class Meta:
        model = SemesterEnrollment
        fields = '__all__'


class JoinSemesterRequestSerializer(serializers.ModelSerializer):
    student_name = serializers.ReadOnlyField(source='student.name')
    college_name = serializers.ReadOnlyField(source='college.name')
    department_name = serializers.ReadOnlyField(source='department.name')
    branch_name = serializers.ReadOnlyField(source='branch.name')
    section_name = serializers.ReadOnlyField(source='section.name')
    semester_number = serializers.ReadOnlyField(source='semester.semester_number')

    class Meta:
        model = JoinSemesterRequest
        fields = [
            'id', 'student', 'student_name', 'college', 'college_name', 
            'department', 'department_name', 'branch', 'branch_name', 
            'section', 'section_name', 'semester', 'semester_number', 
            'status', 'remarks', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'student', 'status', 'created_at', 'updated_at']


class SubjectProgressSerializer(serializers.ModelSerializer):
    subject_name = serializers.ReadOnlyField(source='semester_subject.subject_catalog.name')
    subject_code = serializers.ReadOnlyField(source='semester_subject.subject_catalog.code')

    class Meta:
        model = SubjectProgress
        fields = '__all__'


class SemesterProgressSerializer(serializers.ModelSerializer):
    semester_number = serializers.ReadOnlyField(source='semester.semester_number')

    class Meta:
        model = SemesterProgress
        fields = '__all__'


class SemesterReportSerializer(serializers.ModelSerializer):
    semester_number = serializers.ReadOnlyField(source='semester.semester_number')

    class Meta:
        model = SemesterReport
        fields = '__all__'


class FacultySerializer(serializers.ModelSerializer):
    department_name = serializers.ReadOnlyField(source='department.name')

    class Meta:
        model = Faculty
        fields = '__all__'
