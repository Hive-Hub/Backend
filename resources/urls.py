from django.urls import path
from .views import ResourcesListView, CRResourceUploadView

urlpatterns = [
    path('resources/', ResourcesListView.as_view(), name='api-resources-list'),
    path('cr/resources/upload/', CRResourceUploadView.as_view(), name='api-cr-resources-upload'),
]
