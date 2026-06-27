from django.urls import path
from .views import (
    StudentAssignmentsListView, StudentAssignmentDetailView, StudentAssignmentSubmitView,
    StudentAIAssignmentsListView, StudentQuestionBankListView, CRAssignmentsView, CRGenerateAIQuestionsView
)

urlpatterns = [
    path('student/assignments/', StudentAssignmentsListView.as_view(), name='api-student-assignments-list'),
    path('student/assignments/<int:pk>/', StudentAssignmentDetailView.as_view(), name='api-student-assignments-detail'),
    path('student/assignments/<int:pk>/submit/', StudentAssignmentSubmitView.as_view(), name='api-student-assignments-submit'),
    path('student/ai-assignments/', StudentAIAssignmentsListView.as_view(), name='api-student-ai-assignments'),
    path('student/question-bank/', StudentQuestionBankListView.as_view(), name='api-student-question-bank'),
    path('cr/assignments/', CRAssignmentsView.as_view(), name='api-cr-assignments'),
    path('cr/generate-questions/', CRGenerateAIQuestionsView.as_view(), name='api-cr-generate-questions'),
]
