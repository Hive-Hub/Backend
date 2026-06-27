from django.urls import path
from .views import StudentAnnouncementsView, CRAnnouncementsView

urlpatterns = [
    path('student/announcements/', StudentAnnouncementsView.as_view(), name='api-student-announcements'),
    path('cr/announcements/', CRAnnouncementsView.as_view(), name='api-cr-announcements'),
]
