from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    AgentViewSet, AgentWorkflowViewSet, AgentTaskViewSet, 
    AgentLogViewSet, AgentRunView, SystemHealthViewSet, AgentHealthViewSet,
    DatabaseHealthViewSet, StorageHealthViewSet, APIHealthViewSet,
    StudentAnalyticsViewSet, CRAnalyticsViewSet, AdminAnalyticsViewSet,
    AIAnalyticsViewSet, AlertViewSet, RecommendationViewSet, ReportExportView,
    AgentCapabilityViewSet, WorkflowStepViewSet, TaskDependencyViewSet,
    TaskResultViewSet, AgentExecutionLogViewSet, AgentMetricViewSet,
    AgentWorkflowRunView, AgentHealthView, AgentMetricsView
)

router = DefaultRouter()
# Register tasks, workflows, and logs first
router.register(r'tasks', AgentTaskViewSet, basename='agent-task')
router.register(r'workflows', AgentWorkflowViewSet, basename='agent-workflow')
router.register(r'logs', AgentLogViewSet, basename='agent-log')

# Register monitoring ViewSets
router.register(r'system-health', SystemHealthViewSet, basename='system-health')
router.register(r'agent-health', AgentHealthViewSet, basename='agent-health')
router.register(r'database-health', DatabaseHealthViewSet, basename='database-health')
router.register(r'storage-health', StorageHealthViewSet, basename='storage-health')
router.register(r'api-health', APIHealthViewSet, basename='api-health')
router.register(r'student-analytics', StudentAnalyticsViewSet, basename='student-analytics')
router.register(r'cr-analytics', CRAnalyticsViewSet, basename='cr-analytics')
router.register(r'admin-analytics', AdminAnalyticsViewSet, basename='admin-analytics')
router.register(r'ai-analytics', AIAnalyticsViewSet, basename='ai-analytics')
router.register(r'alerts', AlertViewSet, basename='alert')
router.register(r'recommendations', RecommendationViewSet, basename='recommendation')

# Register new AgentOS ViewSets
router.register(r'capabilities', AgentCapabilityViewSet, basename='capability')
router.register(r'steps', WorkflowStepViewSet, basename='step')
router.register(r'dependencies', TaskDependencyViewSet, basename='dependency')
router.register(r'results', TaskResultViewSet, basename='result')
router.register(r'execution-logs', AgentExecutionLogViewSet, basename='execution-log')
router.register(r'agent-metrics', AgentMetricViewSet, basename='agent-metric')

# Base agent routes mapped at root level of agents app (e.g. /agents/)
router.register(r'', AgentViewSet, basename='agent')

urlpatterns = [
    # Custom post/get views mapped before router to avoid slug conflicts
    path('run/', AgentRunView.as_view(), name='agent-run'),
    path('workflow/run/', AgentWorkflowRunView.as_view(), name='workflow-run'),
    path('health/', AgentHealthView.as_view(), name='agent-health-dashboard'),
    path('metrics/', AgentMetricsView.as_view(), name='agent-metrics-dashboard'),
    path('reports/export/', ReportExportView.as_view(), name='report-export'),
    path('', include(router.urls)),
]
