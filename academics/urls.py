from django.urls import path
from .views import (
    StudentSubjectsView, SubjectUnitsView, UnitTopicsView, 
    StudentScheduleView, StudentProgressView, CRSubjectsView, CRDailyClassReviewsView
)

urlpatterns = [
    path('student/subjects/', StudentSubjectsView.as_view(), name='api-student-subjects'),
    path('student/subjects/<int:pk>/units/', SubjectUnitsView.as_view(), name='api-subject-units'),
    path('student/units/<int:pk>/topics/', UnitTopicsView.as_view(), name='api-unit-topics'),
    path('student/schedule/', StudentScheduleView.as_view(), name='api-student-schedule'),
    path('student/progress/', StudentProgressView.as_view(), name='api-student-progress'),
    path('cr/subjects/', CRSubjectsView.as_view(), name='api-cr-subjects'),
    path('cr/daily-reviews/', CRDailyClassReviewsView.as_view(), name='api-cr-daily-reviews'),
]
