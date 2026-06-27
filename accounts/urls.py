from django.urls import path
from .views import (
    LoginView, StudentProfileView, StudentDashboardView, StudentReportsView,
    StudentNotificationsView, CRDashboardView, CRJoinRequestsView, 
    CRJoinRequestApproveView, CRJoinRequestRejectView, CRStudentProgressView
)

urlpatterns = [
    path('auth/login/', LoginView.as_view(), name='api-auth-login'),
    path('student/profile/', StudentProfileView.as_view(), name='api-student-profile'),
    path('student/dashboard/', StudentDashboardView.as_view(), name='api-student-dashboard'),
    path('student/reports/', StudentReportsView.as_view(), name='api-student-reports'),
    path('student/notifications/', StudentNotificationsView.as_view(), name='api-student-notifications'),
    path('cr/dashboard/', CRDashboardView.as_view(), name='api-cr-dashboard'),
    path('cr/join-requests/', CRJoinRequestsView.as_view(), name='api-cr-join-requests'),
    path('cr/join-requests/<int:pk>/approve/', CRJoinRequestApproveView.as_view(), name='api-cr-join-requests-approve'),
    path('cr/join-requests/<int:pk>/reject/', CRJoinRequestRejectView.as_view(), name='api-cr-join-requests-reject'),
    path('cr/student-progress/', CRStudentProgressView.as_view(), name='api-cr-student-progress'),
]
