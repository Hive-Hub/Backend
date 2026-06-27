from rest_framework import serializers
from .models import (
    Department, Branch, Section, Semester, SubjectCatalog, 
    SemesterSubject, SubjectUnit, SubjectTopic, DailyClassReview, 
    TimetableEntry, Attendance, SemesterCalendar, TopicProgress
)
from accounts.serializers import FacultySerializer


class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = '__all__'


class BranchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Branch
        fields = '__all__'


class SectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Section
        fields = '__all__'


class SemesterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Semester
        fields = '__all__'


class SubjectCatalogSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubjectCatalog
        fields = '__all__'


class SemesterSubjectSerializer(serializers.ModelSerializer):
    name = serializers.ReadOnlyField(source='subject_catalog.name')
    code = serializers.ReadOnlyField(source='subject_catalog.code')
    credits = serializers.ReadOnlyField(source='subject_catalog.credits')

    class Meta:
        model = SemesterSubject
        fields = ['id', 'semester', 'subject_catalog', 'name', 'code', 'credits']


class SubjectTopicSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubjectTopic
        fields = '__all__'


class SubjectUnitSerializer(serializers.ModelSerializer):
    topics = SubjectTopicSerializer(many=True, read_only=True)

    class Meta:
        model = SubjectUnit
        fields = ['id', 'subject_catalog', 'unit_number', 'title', 'description', 'topics']


class TimetableEntrySerializer(serializers.ModelSerializer):
    subject_name = serializers.ReadOnlyField(source='subject.subject_catalog.name')
    subject_code = serializers.ReadOnlyField(source='subject.subject_catalog.code')
    faculty_name = serializers.ReadOnlyField(source='faculty.name')

    class Meta:
        model = TimetableEntry
        fields = '__all__'


class DailyClassReviewSerializer(serializers.ModelSerializer):
    subject_name = serializers.ReadOnlyField(source='semester_subject.subject_catalog.name')
    topics_list = SubjectTopicSerializer(source='topics', many=True, read_only=True)

    class Meta:
        model = DailyClassReview
        fields = [
            'id', 'semester_subject', 'subject_name', 'cr_assignment', 'title', 
            'class_date', 'timetable_entry', 'topics', 'topics_list', 
            'topics_covered', 'faculty_notes', 'important_questions', 
            'exam_hints', 'resources', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class TopicProgressSerializer(serializers.ModelSerializer):
    topic_title = serializers.ReadOnlyField(source='subject_topic.title')

    class Meta:
        model = TopicProgress
        fields = '__all__'


class AttendanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attendance
        fields = '__all__'


class SemesterCalendarSerializer(serializers.ModelSerializer):
    class Meta:
        model = SemesterCalendar
        fields = '__all__'
