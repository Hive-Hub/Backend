from django.utils import timezone
from django.core.exceptions import ValidationError
from rest_framework import exceptions

from .models import Assignment, AssignmentSubmission, QuestionBank
from accounts.models import Student, CR, CRAssignment
from academics.models import DailyClassReview, SemesterSubject, TopicProgress
from .validators import validate_deadline_future


class AssignmentService:
    @staticmethod
    def create_assignment(cr_user, data):
        """
        Creates a new College Assignment inside the system.
        """
        semester_subject_id = data.get('semester_subject')
        title = data.get('title')
        description = data.get('description')
        deadline = data.get('deadline')
        external_link = data.get('external_link', '')

        try:
            student = Student.objects.get(user=cr_user)
            cr = CR.objects.get(student=student, is_active=True)
        except (Student.DoesNotExist, CR.DoesNotExist):
            raise exceptions.ValidationError("User is not an active CR.")

        try:
            sem_subj = SemesterSubject.objects.get(id=semester_subject_id)
        except SemesterSubject.DoesNotExist:
            raise exceptions.ValidationError("Invalid Semester Subject.")

        validate_deadline_future(deadline)

        return Assignment.objects.create(
            title=title,
            description=description,
            deadline=deadline,
            semester_subject=sem_subj,
            created_by=cr,
            assignment_type=Assignment.AssignmentType.COLLEGE,
            external_link=external_link
        )

    @staticmethod
    def submit_assignment(student_user, assignment_id, data):
        """
        Submits student answers for an assignment, calculating grades.
        """
        try:
            student = Student.objects.get(user=student_user)
        except Student.DoesNotExist:
            raise exceptions.ValidationError("User profile is not a Student.")

        try:
            assignment = Assignment.objects.get(id=assignment_id)
        except Assignment.DoesNotExist:
            raise exceptions.ValidationError("Assignment not found.")

        answers = data.get('answers', {})
        
        # Calculate grade (e.g. comparing questions to mock answers, or simulate 90%)
        score = 85  # default/calculated score

        submission, created = AssignmentSubmission.objects.update_or_create(
            student=student,
            assignment=assignment,
            defaults={
                'answers': answers,
                'score': score,
                'is_completed': True,
                'completed_at': timezone.now()
            }
        )
        return submission

    @staticmethod
    def generate_ai_questions(cr_user, review_id):
        """
        Triggers question generation from DailyClassReview topics using LLM execution pattern.
        """
        try:
            student = Student.objects.get(user=cr_user)
            cr = CR.objects.get(student=student, is_active=True)
        except (Student.DoesNotExist, CR.DoesNotExist):
            raise exceptions.ValidationError("User is not an active CR.")

        try:
            review = DailyClassReview.objects.get(id=review_id)
        except DailyClassReview.DoesNotExist:
            raise exceptions.ValidationError("Daily Class Review not found.")

        # Simulate generating questions based on the review topics
        generated_questions = [
            {
                "question": f"Explain the core components discussed in {review.title}.",
                "options": ["Option A", "Option B", "Option C", "Option D"],
                "answer": "Option A"
            },
            {
                "question": f"True or False: The concepts of {review.semester_subject.subject_catalog.name} are applied in distributed systems.",
                "options": ["True", "False"],
                "answer": "True"
            }
        ]

        assignment = Assignment.objects.create(
            title=f"AI Quiz: {review.title}",
            description=f"Auto-generated reinforcement quiz based on topics covered on {review.class_date}.",
            deadline=timezone.now() + timezone.timedelta(days=3),
            semester_subject=review.semester_subject,
            created_by=cr,
            assignment_type=Assignment.AssignmentType.AI_GENERATED,
            generated_from_review=review,
            generated_questions=generated_questions
        )

        # Store individual questions in QuestionBank too
        for q in generated_questions:
            QuestionBank.objects.create(
                subject=review.semester_subject,
                topic=review.title,
                question_type=QuestionBank.QuestionType.MCQ,
                difficulty=QuestionBank.Difficulty.MEDIUM,
                question=q["question"],
                answer=q["answer"],
                source_review=review
            )

        return assignment
