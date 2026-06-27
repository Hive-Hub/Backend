from rest_framework import viewsets, status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import action

from .models import (
    Agent, AgentPrompt, AgentWorkflow, AgentTask,
    AgentExecution, AgentMemory, AgentContext, AgentLog, AgentConfiguration,
    AgentCapability, WorkflowStep, TaskDependency, TaskResult, AgentExecutionLog, AgentMetric
)
from .serializers import (
    AgentSerializer, AgentPromptSerializer, AgentWorkflowSerializer,
    AgentTaskSerializer, AgentExecutionSerializer, AgentLogSerializer,
    AgentCapabilitySerializer, WorkflowStepSerializer, TaskDependencySerializer,
    TaskResultSerializer, AgentExecutionLogSerializer, AgentMetricSerializer
)
from .permissions import IsAgentAdminOrCRReadOnly, IsMonitoringObserverPermission
from .services.workflow_service import WorkflowService
from .registry import AgentRegistry


class AgentViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows agents to be viewed or edited.
    """
    queryset = Agent.objects.all().order_by('name')
    serializer_class = AgentSerializer
    permission_classes = [IsAgentAdminOrCRReadOnly]
    lookup_field = 'slug'

    @action(detail=True, methods=['get', 'post'], url_path='prompts')
    def prompts(self, request, slug=None):
        """
        Manage prompts associated with a specific agent.
        """
        agent = self.get_object()
        if request.method == 'GET':
            prompts = AgentPrompt.objects.filter(agent=agent)
            serializer = AgentPromptSerializer(prompts, many=True)
            return Response(serializer.data)
            
        elif request.method == 'POST':
            # Check write permission (Admins only)
            if not (request.user.is_superuser or request.user.is_staff or getattr(request.user, 'role', None) == 'ADMIN'):
                return Response(
                    {"detail": "You do not have permission to perform this action."},
                    status=status.HTTP_403_FORBIDDEN
                )
                
            serializer = AgentPromptSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save(agent=agent)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AgentWorkflowViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows workflows to be viewed.
    """
    queryset = AgentWorkflow.objects.all().order_by('name')
    serializer_class = AgentWorkflowSerializer
    permission_classes = [IsAgentAdminOrCRReadOnly]


class AgentTaskViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows tasks to be viewed or created.
    """
    queryset = AgentTask.objects.all().order_by('-created_at')
    serializer_class = AgentTaskSerializer
    permission_classes = [IsAgentAdminOrCRReadOnly]

    def perform_create(self, serializer):
        # Save user who created the task
        serializer.save(created_by=self.request.user)


class AgentLogViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows logs to be viewed.
    """
    queryset = AgentLog.objects.all().order_by('-timestamp')
    serializer_class = AgentLogSerializer
    permission_classes = [IsAgentAdminOrCRReadOnly]


class AgentRunView(APIView):
    """
    Custom POST API view to run workflow tasks.
    POST /agents/run/
    Payload:
    - task_id (int, optional)
    - workflow_id (int, optional)
    - title (str, conditional if task_id not provided)
    - description (str, conditional if task_id not provided)
    - priority (str, optional, defaults to MEDIUM)
    """
    permission_classes = [IsAgentAdminOrCRReadOnly]

    def post(self, request, *args, **kwargs):
        task_id = request.data.get('task_id')
        workflow_id = request.data.get('workflow_id')

        # 1. Resolve or dynamically create the Task
        if not task_id:
            title = request.data.get('title')
            description = request.data.get('description')
            priority = request.data.get('priority', AgentTask.Priority.MEDIUM)

            if not title or not description:
                return Response(
                    {"error": "Please provide 'task_id' or both 'title' and 'description' to create a task."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Ensure defaults are set up first
            AgentRegistry.setup_defaults()

            task = AgentTask.objects.create(
                title=title,
                description=description,
                priority=priority,
                created_by=request.user
            )
            task_id = task.id
        else:
            try:
                task = AgentTask.objects.get(id=task_id)
            except AgentTask.DoesNotExist:
                return Response(
                    {"error": f"Task with id {task_id} not found"},
                    status=status.HTTP_404_NOT_FOUND
                )

        # 2. Resolve or fallback to default Workflow
        if not workflow_id:
            # Setup defaults if missing
            AgentRegistry.setup_defaults()
            default_wf = AgentWorkflow.objects.filter(active=True).first()
            if not default_wf:
                return Response(
                    {"error": "No active workflow found in system database."},
                    status=status.HTTP_404_NOT_FOUND
                )
            workflow_id = default_wf.id
        else:
            try:
                workflow = AgentWorkflow.objects.get(id=workflow_id)
            except AgentWorkflow.DoesNotExist:
                return Response(
                    {"error": f"Workflow with id {workflow_id} not found"},
                    status=status.HTTP_404_NOT_FOUND
                )

        # 3. Trigger execution flow
        result = WorkflowService.run_task_in_workflow(task_id, workflow_id)
        
        if not result.get("success"):
            return Response(result, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
        return Response(result, status=status.HTTP_200_OK)


# --- MONITORING VIEWSETS & EXPORTS ---

from django.db.models import Q
from django.http import HttpResponse
from .services.monitoring_service import MonitoringService
from .models import (
    SystemHealth, AgentHealth, DatabaseHealth, StorageHealth, APIHealth,
    StudentAnalytics, CRAnalytics, AdminAnalytics, AIAnalytics, Alert, Recommendation
)
from .serializers import (
    SystemHealthSerializer, AgentHealthSerializer, DatabaseHealthSerializer,
    StorageHealthSerializer, APIHealthSerializer, StudentAnalyticsSerializer,
    CRAnalyticsSerializer, AdminAnalyticsSerializer, AIAnalyticsSerializer,
    AlertSerializer, RecommendationSerializer
)


class SystemHealthViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = SystemHealthSerializer
    permission_classes = [IsMonitoringObserverPermission]

    def get_queryset(self):
        user = self.request.user
        role = getattr(user, 'role', None)
        if user.is_superuser or user.is_staff or role == 'ADMIN':
            return SystemHealth.objects.all().order_by('-timestamp')
        return SystemHealth.objects.none()


class AgentHealthViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = AgentHealthSerializer
    permission_classes = [IsMonitoringObserverPermission]

    def get_queryset(self):
        user = self.request.user
        role = getattr(user, 'role', None)
        if user.is_superuser or user.is_staff or role == 'ADMIN':
            return AgentHealth.objects.all().order_by('-timestamp')
        return AgentHealth.objects.none()


class DatabaseHealthViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = DatabaseHealthSerializer
    permission_classes = [IsMonitoringObserverPermission]

    def get_queryset(self):
        user = self.request.user
        role = getattr(user, 'role', None)
        if user.is_superuser or user.is_staff or role == 'ADMIN':
            return DatabaseHealth.objects.all().order_by('-timestamp')
        return DatabaseHealth.objects.none()


class StorageHealthViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = StorageHealthSerializer
    permission_classes = [IsMonitoringObserverPermission]

    def get_queryset(self):
        user = self.request.user
        role = getattr(user, 'role', None)
        if user.is_superuser or user.is_staff or role == 'ADMIN':
            return StorageHealth.objects.all().order_by('-timestamp')
        return StorageHealth.objects.none()


class APIHealthViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = APIHealthSerializer
    permission_classes = [IsMonitoringObserverPermission]

    def get_queryset(self):
        user = self.request.user
        role = getattr(user, 'role', None)
        if user.is_superuser or user.is_staff or role == 'ADMIN':
            return APIHealth.objects.all().order_by('-timestamp')
        return APIHealth.objects.none()


class StudentAnalyticsViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = StudentAnalyticsSerializer
    permission_classes = [IsMonitoringObserverPermission]

    def get_queryset(self):
        user = self.request.user
        role = getattr(user, 'role', None)
        if user.is_superuser or user.is_staff or role == 'ADMIN':
            return StudentAnalytics.objects.all().order_by('-timestamp')
            
        elif role == 'CR':
            # Retrieve active sections CR manages
            active_sections = list(user.student_profile.cr_assignments.filter(is_active=True).values_list('section_id', flat=True))
            cr_profile = getattr(user.student_profile, 'cr', None)
            if not active_sections and cr_profile and cr_profile.student.section_id:
                active_sections = [cr_profile.student.section_id]
            return StudentAnalytics.objects.filter(student__section_id__in=active_sections).order_by('-timestamp')
            
        elif role == 'STUDENT':
            student_profile = getattr(user, 'student_profile', None)
            if student_profile:
                return StudentAnalytics.objects.filter(student=student_profile).order_by('-timestamp')
                
        return StudentAnalytics.objects.none()


class CRAnalyticsViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = CRAnalyticsSerializer
    permission_classes = [IsMonitoringObserverPermission]

    def get_queryset(self):
        user = self.request.user
        role = getattr(user, 'role', None)
        if user.is_superuser or user.is_staff or role == 'ADMIN':
            return CRAnalytics.objects.all().order_by('-timestamp')
            
        elif role == 'CR':
            cr_profile = getattr(user.student_profile, 'cr', None)
            if cr_profile:
                return CRAnalytics.objects.filter(cr=cr_profile).order_by('-timestamp')
                
        return CRAnalytics.objects.none()


class AdminAnalyticsViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = AdminAnalyticsSerializer
    permission_classes = [IsMonitoringObserverPermission]

    def get_queryset(self):
        user = self.request.user
        role = getattr(user, 'role', None)
        if user.is_superuser or user.is_staff or role == 'ADMIN':
            return AdminAnalytics.objects.all().order_by('-timestamp')
        return AdminAnalytics.objects.none()


class AIAnalyticsViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = AIAnalyticsSerializer
    permission_classes = [IsMonitoringObserverPermission]

    def get_queryset(self):
        user = self.request.user
        role = getattr(user, 'role', None)
        if user.is_superuser or user.is_staff or role == 'ADMIN':
            return AIAnalytics.objects.all().order_by('-timestamp')
        return AIAnalytics.objects.none()


class AlertViewSet(viewsets.ModelViewSet):
    serializer_class = AlertSerializer
    permission_classes = [IsMonitoringObserverPermission]

    def get_queryset(self):
        user = self.request.user
        role = getattr(user, 'role', None)
        if user.is_superuser or user.is_staff or role == 'ADMIN':
            return Alert.objects.all().order_by('-created_at')
            
        elif role == 'CR':
            active_sections = list(user.student_profile.cr_assignments.filter(is_active=True).values_list('section_id', flat=True))
            cr_profile = getattr(user.student_profile, 'cr', None)
            if not active_sections and cr_profile and cr_profile.student.section_id:
                active_sections = [cr_profile.student.section_id]
            return Alert.objects.filter(
                Q(section_id__in=active_sections) | 
                Q(student__section_id__in=active_sections)
            ).order_by('-created_at')
            
        elif role == 'STUDENT':
            student_profile = getattr(user, 'student_profile', None)
            if student_profile:
                return Alert.objects.filter(student=student_profile).order_by('-created_at')
                
        return Alert.objects.none()


class RecommendationViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = RecommendationSerializer
    permission_classes = [IsMonitoringObserverPermission]

    def get_queryset(self):
        user = self.request.user
        role = getattr(user, 'role', None)
        if user.is_superuser or user.is_staff or role == 'ADMIN':
            return Recommendation.objects.all().order_by('-created_at')
            
        elif role == 'CR':
            active_sections = list(user.student_profile.cr_assignments.filter(is_active=True).values_list('section_id', flat=True))
            cr_profile = getattr(user.student_profile, 'cr', None)
            if not active_sections and cr_profile and cr_profile.student.section_id:
                active_sections = [cr_profile.student.section_id]
            return Recommendation.objects.filter(
                Q(section_id__in=active_sections) | 
                Q(student__section_id__in=active_sections)
            ).order_by('-created_at')
            
        elif role == 'STUDENT':
            student_profile = getattr(user, 'student_profile', None)
            if student_profile:
                return Recommendation.objects.filter(student=student_profile).order_by('-created_at')
                
        return Recommendation.objects.none()


class ReportExportView(APIView):
    """
    API endpoint to export monitoring logs to CSV, Excel, or PDF structures.
    GET /agents/reports/export/?format=csv&metric=student_analytics
    """
    permission_classes = [IsMonitoringObserverPermission]

    def dispatch(self, request, *args, **kwargs):
        print("DEBUG DISPATCH: ReportExportView.dispatch called!")
        print("QUERY PARAMS IN VIEW GET:", request.GET)
        try:
            return super().dispatch(request, *args, **kwargs)
        except Exception as e:
            print("DEBUG DISPATCH EXCEPTION:", str(e))
            raise e

    def handle_exception(self, exc):
        print("DEBUG HANDLE_EXCEPTION:", type(exc), str(exc))
        import traceback
        traceback.print_exc()
        return super().handle_exception(exc)

    def get(self, request, *args, **kwargs):
        print("ROUTE MATCHED: Executing ReportExportView.get")
        user = request.user
        role = getattr(user, 'role', None)
        
        # Get params
        export_format = request.query_params.get('export_format', 'csv').lower().strip()
        metric = request.query_params.get('metric', 'student_analytics').lower().strip()

        # Resolve querysets based on permissions (CR/Student vs Admin scope)
        if metric == 'student_analytics':
            fields = ['id', 'student_id', 'dashboard_load_time', 'assignment_completion_rate', 'experience_score', 'progress_status', 'timestamp']
            
            if user.is_superuser or user.is_staff or role == 'ADMIN':
                queryset = StudentAnalytics.objects.all()
            elif role == 'CR':
                active_sections = list(user.student_profile.cr_assignments.filter(is_active=True).values_list('section_id', flat=True))
                cr_profile = getattr(user.student_profile, 'cr', None)
                if not active_sections and cr_profile and cr_profile.student.section_id:
                    active_sections = [cr_profile.student.section_id]
                queryset = StudentAnalytics.objects.filter(student__section_id__in=active_sections)
            elif role == 'STUDENT':
                queryset = StudentAnalytics.objects.filter(student=getattr(user, 'student_profile', None))
            else:
                queryset = StudentAnalytics.objects.none()

        elif metric == 'alerts':
            fields = ['id', 'title', 'message', 'alert_type', 'severity', 'is_resolved', 'created_at']
            
            if user.is_superuser or user.is_staff or role == 'ADMIN':
                queryset = Alert.objects.all()
            elif role == 'CR':
                active_sections = list(user.student_profile.cr_assignments.filter(is_active=True).values_list('section_id', flat=True))
                cr_profile = getattr(user.student_profile, 'cr', None)
                if not active_sections and cr_profile and cr_profile.student.section_id:
                    active_sections = [cr_profile.student.section_id]
                queryset = Alert.objects.filter(Q(section_id__in=active_sections) | Q(student__section_id__in=active_sections))
            elif role == 'STUDENT':
                queryset = Alert.objects.filter(student=getattr(user, 'student_profile', None))
            else:
                queryset = Alert.objects.none()

        elif metric == 'system_health' and (user.is_superuser or user.is_staff or role == 'ADMIN'):
            fields = ['id', 'overall_status', 'cpu_usage', 'memory_usage', 'active_connections', 'timestamp']
            queryset = SystemHealth.objects.all()
            
        else:
            return Response(
                {"error": "Unauthorized metric resource or invalid query configurations."},
                status=status.HTTP_403_FORBIDDEN
            )

        queryset = queryset.order_by('-id')[:100]

        # Generate response formats
        if export_format == 'csv':
            csv_data = MonitoringService.export_csv_to_string(queryset, fields)
            response = HttpResponse(csv_data, content_type='text/csv')
            response['Content-Disposition'] = f'attachment; filename="{metric}_report.csv"'
            return response
            
        elif export_format == 'excel':
            excel_data = MonitoringService.export_excel_html_string(queryset, fields)
            response = HttpResponse(excel_data, content_type='application/vnd.ms-excel')
            response['Content-Disposition'] = f'attachment; filename="{metric}_report.xls"'
            return response
            
        elif export_format == 'pdf':
            # Returns print-ready styled HTML layout representation
            pdf_html = MonitoringService.export_pdf_html_string(queryset, fields, title=f"{metric.replace('_', ' ').title()} Report")
            response = HttpResponse(pdf_html, content_type='text/html')
            response['Content-Disposition'] = f'attachment; filename="{metric}_report.html"'
            return response

        return Response(
            {"error": f"Invalid format '{export_format}'. Supported formats: csv, excel, pdf."},
            status=status.HTTP_400_BAD_REQUEST
        )


class AgentCapabilityViewSet(viewsets.ModelViewSet):
    queryset = AgentCapability.objects.all()
    serializer_class = AgentCapabilitySerializer
    permission_classes = [IsMonitoringObserverPermission]


class WorkflowStepViewSet(viewsets.ModelViewSet):
    queryset = WorkflowStep.objects.all().order_by('step_number')
    serializer_class = WorkflowStepSerializer
    permission_classes = [IsMonitoringObserverPermission]


class TaskDependencyViewSet(viewsets.ModelViewSet):
    queryset = TaskDependency.objects.all()
    serializer_class = TaskDependencySerializer
    permission_classes = [IsMonitoringObserverPermission]


class TaskResultViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = TaskResult.objects.all()
    serializer_class = TaskResultSerializer
    permission_classes = [IsMonitoringObserverPermission]


class AgentExecutionLogViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = AgentExecutionLog.objects.all().order_by('-timestamp')
    serializer_class = AgentExecutionLogSerializer
    permission_classes = [IsMonitoringObserverPermission]


class AgentMetricViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = AgentMetric.objects.all().order_by('-timestamp')
    serializer_class = AgentMetricSerializer
    permission_classes = [IsMonitoringObserverPermission]


class AgentWorkflowRunView(APIView):
    """
    POST /agents/workflow/run/
    Payload:
    - user_request (str)
    """
    permission_classes = [IsMonitoringObserverPermission]

    def post(self, request, *args, **kwargs):
        user_request = request.data.get('user_request')
        if not user_request:
            return Response(
                {"error": "Please provide 'user_request' parameter."},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        from .orchestrator import Orchestrator
        orchestrator = Orchestrator()
        result = orchestrator.handle_request(user_request)
        return Response(result, status=status.HTTP_200_OK)


class AgentHealthView(APIView):
    """
    GET /agents/health/
    Consolidated health dashboard summary.
    """
    permission_classes = [IsMonitoringObserverPermission]

    def get(self, request, *args, **kwargs):
        from .health import HealthMonitor
        sys_h = HealthMonitor.audit_system()
        db_h = HealthMonitor.audit_database()
        storage_h = HealthMonitor.audit_storage()
        api_h = HealthMonitor.audit_api()
        
        return Response({
            "status": sys_h.overall_status,
            "cpu_usage": sys_h.cpu_usage,
            "memory_usage": sys_h.memory_usage,
            "database": {
                "connections": db_h.connections_count,
                "slow_queries": db_h.slow_queries_count,
                "migration_status": db_h.migration_status
            },
            "storage": {
                "bucket_name": storage_h.bucket_name,
                "file_count": storage_h.file_count,
                "size_bytes": storage_h.storage_size_bytes
            },
            "api_performance": {
                "endpoint": api_h.endpoint,
                "avg_response_time_ms": api_h.avg_response_time,
                "success_rate": api_h.success_rate
            }
        }, status=status.HTTP_200_OK)


class AgentMetricsView(APIView):
    """
    GET /agents/metrics/
    Consolidated metrics summary.
    """
    permission_classes = [IsMonitoringObserverPermission]

    def get(self, request, *args, **kwargs):
        from .models import AgentMetric, TaskResult
        from django.db.models import Sum, Avg
        
        total_tokens = TaskResult.objects.aggregate(Sum('tokens_used'))['tokens_used__sum'] or 0
        avg_exec_time = TaskResult.objects.aggregate(Avg('execution_time'))['execution_time__avg'] or 0.0
        
        agent_metrics = []
        for agent in Agent.objects.filter(is_active=True):
            avg_agent_tokens = TaskResult.objects.filter(task__assigned_agent=agent).aggregate(Sum('tokens_used'))['tokens_used__sum'] or 0
            agent_metrics.append({
                "agent_name": agent.name,
                "slug": agent.slug,
                "status": agent.status,
                "tokens_consumed": avg_agent_tokens
            })
            
        return Response({
            "total_tokens_consumed": total_tokens,
            "average_execution_time_seconds": avg_exec_time,
            "agent_performance": agent_metrics
        }, status=status.HTTP_200_OK)


