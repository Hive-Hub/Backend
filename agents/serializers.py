from rest_framework import serializers
from .models import (
    Agent, AgentPrompt, AgentWorkflow, AgentTask,
    AgentExecution, AgentMemory, AgentContext, AgentLog, AgentConfiguration,
    AgentCapability, WorkflowStep, TaskDependency, TaskResult, AgentExecutionLog, AgentMetric
)


class AgentPromptSerializer(serializers.ModelSerializer):
    class Meta:
        model = AgentPrompt
        fields = ['id', 'agent', 'system_prompt', 'developer_prompt', 'user_template', 'version', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class AgentConfigurationSerializer(serializers.ModelSerializer):
    class Meta:
        model = AgentConfiguration
        fields = ['id', 'agent', 'config_key', 'config_value', 'is_secret', 'updated_at']
        read_only_fields = ['id', 'updated_at']

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        # Redact secrets for security
        if instance.is_secret:
            ret['config_value'] = '********'
        return ret


class AgentMemorySerializer(serializers.ModelSerializer):
    class Meta:
        model = AgentMemory
        fields = ['id', 'agent', 'memory_key', 'memory_value', 'updated_at']
        read_only_fields = ['id', 'updated_at']


class AgentContextSerializer(serializers.ModelSerializer):
    class Meta:
        model = AgentContext
        fields = ['id', 'agent', 'context_key', 'context_value', 'updated_at']
        read_only_fields = ['id', 'updated_at']


class AgentSerializer(serializers.ModelSerializer):
    prompts = AgentPromptSerializer(many=True, read_only=True)
    configurations = AgentConfigurationSerializer(many=True, read_only=True)

    class Meta:
        model = Agent
        fields = [
            'id', 'name', 'slug', 'description', 'agent_type', 
            'status', 'version', 'is_active', 'created_at', 'updated_at',
            'prompts', 'configurations'
        ]
        read_only_fields = ['id', 'slug', 'created_at', 'updated_at']


class AgentWorkflowSerializer(serializers.ModelSerializer):
    class Meta:
        model = AgentWorkflow
        fields = ['id', 'name', 'description', 'steps', 'active', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class AgentTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = AgentTask
        fields = [
            'id', 'title', 'description', 'priority', 'status', 
            'assigned_agent', 'created_by', 'approval_required', 'is_approved',
            'created_at', 'completed_at'
        ]
        read_only_fields = ['id', 'created_by', 'created_at', 'completed_at']


class AgentLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = AgentLog
        fields = ['id', 'execution', 'agent', 'level', 'message', 'timestamp']
        read_only_fields = ['id', 'timestamp']


class AgentExecutionSerializer(serializers.ModelSerializer):
    logs = AgentLogSerializer(many=True, read_only=True)

    class Meta:
        model = AgentExecution
        fields = [
            'id', 'task', 'agent', 'input', 'output', 'execution_time', 
            'status', 'tokens_used', 'started_at', 'finished_at', 'error_message',
            'logs'
        ]
        read_only_fields = ['id', 'started_at', 'finished_at', 'execution_time', 'tokens_used', 'logs']


# --- MONITORING SERIALIZERS ---

from .models import (
    SystemHealth, AgentHealth, DatabaseHealth, StorageHealth, APIHealth,
    StudentAnalytics, CRAnalytics, AdminAnalytics, AIAnalytics, Alert, Recommendation
)


class SystemHealthSerializer(serializers.ModelSerializer):
    class Meta:
        model = SystemHealth
        fields = '__all__'


class AgentHealthSerializer(serializers.ModelSerializer):
    class Meta:
        model = AgentHealth
        fields = '__all__'


class DatabaseHealthSerializer(serializers.ModelSerializer):
    class Meta:
        model = DatabaseHealth
        fields = '__all__'


class StorageHealthSerializer(serializers.ModelSerializer):
    class Meta:
        model = StorageHealth
        fields = '__all__'


class APIHealthSerializer(serializers.ModelSerializer):
    class Meta:
        model = APIHealth
        fields = '__all__'


class StudentAnalyticsSerializer(serializers.ModelSerializer):
    student_name = serializers.ReadOnlyField(source='student.name')

    class Meta:
        model = StudentAnalytics
        fields = '__all__'


class CRAnalyticsSerializer(serializers.ModelSerializer):
    cr_name = serializers.ReadOnlyField(source='cr.student.name')
    section_name = serializers.ReadOnlyField(source='section.name')

    class Meta:
        model = CRAnalytics
        fields = '__all__'


class AdminAnalyticsSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdminAnalytics
        fields = '__all__'


class AIAnalyticsSerializer(serializers.ModelSerializer):
    class Meta:
        model = AIAnalytics
        fields = '__all__'


class AlertSerializer(serializers.ModelSerializer):
    student_name = serializers.ReadOnlyField(source='student.name')
    section_name = serializers.ReadOnlyField(source='section.name')

    class Meta:
        model = Alert
        fields = '__all__'


class RecommendationSerializer(serializers.ModelSerializer):
    student_name = serializers.ReadOnlyField(source='student.name')
    section_name = serializers.ReadOnlyField(source='section.name')

    class Meta:
        model = Recommendation
        fields = '__all__'


class AgentCapabilitySerializer(serializers.ModelSerializer):
    class Meta:
        model = AgentCapability
        fields = '__all__'


class WorkflowStepSerializer(serializers.ModelSerializer):
    agent_name = serializers.ReadOnlyField(source='agent.name')

    class Meta:
        model = WorkflowStep
        fields = '__all__'


class TaskDependencySerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskDependency
        fields = '__all__'


class TaskResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskResult
        fields = '__all__'


class AgentExecutionLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = AgentExecutionLog
        fields = '__all__'


class AgentMetricSerializer(serializers.ModelSerializer):
    class Meta:
        model = AgentMetric
        fields = '__all__'

