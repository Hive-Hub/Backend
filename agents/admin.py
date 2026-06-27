from django.contrib import admin
from .models import (
    Agent, AgentPrompt, AgentWorkflow, AgentTask,
    AgentExecution, AgentMemory, AgentContext, AgentLog, AgentConfiguration,
    AgentCapability, WorkflowStep, TaskDependency, TaskResult, AgentExecutionLog, AgentMetric
)


class AgentPromptInline(admin.StackedInline):
    model = AgentPrompt
    extra = 0


class AgentConfigurationInline(admin.TabularInline):
    model = AgentConfiguration
    extra = 0


@admin.register(Agent)
class AgentAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'agent_type', 'status', 'version', 'is_active', 'created_at')
    search_fields = ('name', 'slug', 'description')
    list_filter = ('agent_type', 'status', 'is_active', 'created_at')
    prepopulated_fields = {'slug': ('name',)}
    inlines = [AgentPromptInline, AgentConfigurationInline]


@admin.register(AgentPrompt)
class AgentPromptAdmin(admin.ModelAdmin):
    list_display = ('agent', 'version', 'created_at', 'updated_at')
    search_fields = ('agent__name', 'system_prompt', 'developer_prompt')
    list_filter = ('created_at', 'updated_at')


@admin.register(AgentWorkflow)
class AgentWorkflowAdmin(admin.ModelAdmin):
    list_display = ('name', 'active', 'created_at', 'updated_at')
    search_fields = ('name', 'description')
    list_filter = ('active', 'created_at')


class AgentExecutionInline(admin.TabularInline):
    model = AgentExecution
    extra = 0
    readonly_fields = ('started_at', 'finished_at', 'execution_time', 'tokens_used')


@admin.register(AgentTask)
class AgentTaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'priority', 'status', 'assigned_agent', 'created_by', 'created_at', 'completed_at')
    search_fields = ('title', 'description', 'created_by__username')
    list_filter = ('priority', 'status', 'created_at', 'completed_at')
    inlines = [AgentExecutionInline]


@admin.register(AgentExecution)
class AgentExecutionAdmin(admin.ModelAdmin):
    list_display = ('id', 'task', 'agent', 'status', 'execution_time', 'tokens_used', 'started_at')
    search_fields = ('task__title', 'agent__name', 'error_message')
    list_filter = ('status', 'started_at', 'finished_at')
    readonly_fields = ('started_at', 'finished_at', 'execution_time', 'tokens_used')


@admin.register(AgentMemory)
class AgentMemoryAdmin(admin.ModelAdmin):
    list_display = ('agent', 'memory_key', 'updated_at')
    search_fields = ('agent__name', 'memory_key', 'memory_value')
    list_filter = ('updated_at',)


@admin.register(AgentContext)
class AgentContextAdmin(admin.ModelAdmin):
    list_display = ('agent', 'context_key', 'updated_at')
    search_fields = ('agent__name', 'context_key', 'context_value')
    list_filter = ('updated_at',)


@admin.register(AgentLog)
class AgentLogAdmin(admin.ModelAdmin):
    list_display = ('execution', 'agent', 'level', 'timestamp', 'message_snippet')
    search_fields = ('agent__name', 'message', 'level')
    list_filter = ('level', 'timestamp')

    def message_snippet(self, obj):
        return obj.message[:75] + '...' if len(obj.message) > 75 else obj.message
    message_snippet.short_description = "Message"


@admin.register(AgentConfiguration)
class AgentConfigurationAdmin(admin.ModelAdmin):
    list_display = ('agent', 'config_key', 'is_secret', 'updated_at')
    search_fields = ('agent__name', 'config_key')
    list_filter = ('is_secret', 'updated_at')


# --- MONITORING ADMIN REGISTRATIONS ---

from .models import (
    SystemHealth, AgentHealth, DatabaseHealth, StorageHealth, APIHealth,
    StudentAnalytics, CRAnalytics, AdminAnalytics, AIAnalytics, Alert, Recommendation
)


@admin.register(SystemHealth)
class SystemHealthAdmin(admin.ModelAdmin):
    list_display = ('overall_status', 'cpu_usage', 'memory_usage', 'active_connections', 'timestamp')
    list_filter = ('overall_status', 'timestamp')


@admin.register(AgentHealth)
class AgentHealthAdmin(admin.ModelAdmin):
    list_display = ('agent', 'status', 'avg_response_time', 'avg_execution_time', 'error_count', 'timestamp')
    list_filter = ('status', 'timestamp')


@admin.register(DatabaseHealth)
class DatabaseHealthAdmin(admin.ModelAdmin):
    list_display = ('connections_count', 'slow_queries_count', 'cache_hit_ratio', 'migration_status', 'timestamp')
    list_filter = ('migration_status', 'timestamp')


@admin.register(StorageHealth)
class StorageHealthAdmin(admin.ModelAdmin):
    list_display = ('bucket_name', 'storage_size_bytes', 'file_count', 'broken_urls_count', 'timestamp')
    list_filter = ('bucket_name', 'timestamp')


@admin.register(APIHealth)
class APIHealthAdmin(admin.ModelAdmin):
    list_display = ('endpoint', 'avg_response_time', 'success_rate', 'traffic_count', 'timestamp')
    list_filter = ('endpoint', 'timestamp')


@admin.register(StudentAnalytics)
class StudentAnalyticsAdmin(admin.ModelAdmin):
    list_display = ('student', 'assignment_completion_rate', 'experience_score', 'progress_status', 'timestamp')
    list_filter = ('progress_status', 'timestamp')
    search_fields = ('student__name',)


@admin.register(CRAnalytics)
class CRAnalyticsAdmin(admin.ModelAdmin):
    list_display = ('cr', 'section', 'pending_join_requests', 'daily_reviews_submitted', 'timestamp')
    list_filter = ('section', 'timestamp')


@admin.register(AdminAnalytics)
class AdminAnalyticsAdmin(admin.ModelAdmin):
    list_display = ('college_growth_rate', 'student_count', 'faculty_count', 'total_api_calls', 'timestamp')
    list_filter = ('timestamp',)


@admin.register(AIAnalytics)
class AIAnalyticsAdmin(admin.ModelAdmin):
    list_display = ('questions_generated', 'embedding_count', 'ai_accuracy', 'avg_generation_time', 'timestamp')
    list_filter = ('timestamp',)


@admin.register(Alert)
class AlertAdmin(admin.ModelAdmin):
    list_display = ('title', 'alert_type', 'severity', 'is_resolved', 'created_at', 'resolved_at')
    list_filter = ('alert_type', 'severity', 'is_resolved', 'created_at')
    search_fields = ('title', 'message')


@admin.register(Recommendation)
class RecommendationAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'created_at')
    list_filter = ('category', 'created_at')
    search_fields = ('title', 'message')


@admin.register(AgentCapability)
class AgentCapabilityAdmin(admin.ModelAdmin):
    list_display = ('agent', 'capability_name', 'created_at')
    search_fields = ('agent__name', 'capability_name')
    list_filter = ('created_at',)


@admin.register(WorkflowStep)
class WorkflowStepAdmin(admin.ModelAdmin):
    list_display = ('workflow', 'step_number', 'name', 'agent', 'status')
    search_fields = ('workflow__name', 'name', 'agent__name')
    list_filter = ('status', 'workflow')


@admin.register(TaskDependency)
class TaskDependencyAdmin(admin.ModelAdmin):
    list_display = ('task', 'depends_on')
    search_fields = ('task__title', 'depends_on__title')


@admin.register(TaskResult)
class TaskResultAdmin(admin.ModelAdmin):
    list_display = ('task', 'status', 'execution_time', 'tokens_used', 'created_at')
    search_fields = ('task__title', 'status')
    list_filter = ('status', 'created_at')


@admin.register(AgentExecutionLog)
class AgentExecutionLogAdmin(admin.ModelAdmin):
    list_display = ('execution', 'level', 'timestamp')
    search_fields = ('execution__task__title', 'message')
    list_filter = ('level', 'timestamp')


@admin.register(AgentMetric)
class AgentMetricAdmin(admin.ModelAdmin):
    list_display = ('agent', 'metric_key', 'metric_value', 'timestamp')
    search_fields = ('agent__name', 'metric_key')
    list_filter = ('metric_key', 'timestamp')

