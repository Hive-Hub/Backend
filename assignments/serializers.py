from rest_framework import serializers
from .models import Assignment, QuestionBank, AssignmentSubmission


class AssignmentSerializer(serializers.ModelSerializer):
    subject_name = serializers.ReadOnlyField(source='semester_subject.subject_catalog.name')

    class Meta:
        model = Assignment
        fields = [
            'id', 'title', 'description', 'deadline', 'semester_subject', 'subject_name', 
            'created_by', 'created_at', 'assignment_type', 'external_link', 
            'start_date', 'end_date', 'generated_from_review', 'difficulty', 
            'topic', 'generated_questions'
        ]
        read_only_fields = ['id', 'created_by', 'created_at']


class AssignmentSubmissionSerializer(serializers.ModelSerializer):
    student_name = serializers.ReadOnlyField(source='student.name')
    assignment_title = serializers.ReadOnlyField(source='assignment.title')

    class Meta:
        model = AssignmentSubmission
        fields = ['id', 'student', 'student_name', 'assignment', 'assignment_title', 'completed_at', 'is_completed', 'score', 'answers']
        read_only_fields = ['id', 'completed_at', 'student']


class QuestionBankSerializer(serializers.ModelSerializer):
    subject_name = serializers.ReadOnlyField(source='subject.subject_catalog.name')

    class Meta:
        model = QuestionBank
        fields = '__all__'
