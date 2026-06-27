from django.db import models
from django.conf import settings
from django.utils.text import slugify


class Agent(models.Model):
    class AgentType(models.TextChoices):
        ORCHESTRATOR = 'ORCHESTRATOR', 'Orchestrator Agent'
        PROJECT_MANAGER = 'PROJECT_MANAGER', 'Project Manager'
        DATABASE_ARCHITECT = 'DATABASE_ARCHITECT', 'Database Architect'
        BACKEND_API = 'BACKEND_API', 'Backend API'
        AUTHENTICATION = 'AUTHENTICATION', 'Authentication'
        STORAGE = 'STORAGE', 'Storage'
        AI_LEARNING = 'AI_LEARNING', 'AI Learning Agent'
        TESTING = 'TESTING', 'Testing Agent'
        DOCUMENTATION = 'DOCUMENTATION', 'Documentation Agent'
        REVIEW = 'REVIEW', 'Review Agent'
        MONITORING = 'MONITORING', 'Monitoring & Intelligence Agent'

    class Status(models.TextChoices):
        IDLE = 'IDLE', 'Idle'
        BUSY = 'BUSY', 'Busy'
        ERROR = 'ERROR', 'Error'

    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    agent_type = models.CharField(
        max_length=50,
        choices=AgentType.choices,
        default=AgentType.PROJECT_MANAGER
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.IDLE
    )
    version = models.CharField(max_length=20, default='1.0.0')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.get_agent_type_display()}) v{self.version}"


class AgentPrompt(models.Model):
    agent = models.ForeignKey(Agent, on_delete=models.CASCADE, related_name='prompts')
    system_prompt = models.TextField()
    developer_prompt = models.TextField(blank=True)
    user_template = models.TextField(blank=True)
    version = models.CharField(max_length=20, default='1.0.0')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Prompt for {self.agent.name} v{self.version}"


class AgentWorkflow(models.Model):
    name = models.CharField(max_length=150)
    description = models.TextField(blank=True)
    steps = models.JSONField(
        default=list,
        help_text="Ordered list of execution steps. E.g., [{'step_number': 1, 'agent_slug': 'project-manager'}]"
    )
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class AgentTask(models.Model):
    class Priority(models.TextChoices):
        LOW = 'LOW', 'Low'
        MEDIUM = 'MEDIUM', 'Medium'
        HIGH = 'HIGH', 'High'

    class Status(models.TextChoices):
        PENDING = 'PENDING', 'Pending'
        IN_PROGRESS = 'IN_PROGRESS', 'In Progress'
        COMPLETED = 'COMPLETED', 'Completed'
        FAILED = 'FAILED', 'Failed'
        AWAITING_APPROVAL = 'AWAITING_APPROVAL', 'Awaiting Approval'

    title = models.CharField(max_length=255)
    description = models.TextField()
    priority = models.CharField(
        max_length=20,
        choices=Priority.choices,
        default=Priority.MEDIUM
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING
    )
    assigned_agent = models.ForeignKey(
        Agent,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_tasks'
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_tasks'
    )
    approval_required = models.BooleanField(default=False)
    is_approved = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Task: {self.title} ({self.status})"


class AgentExecution(models.Model):
    class Status(models.TextChoices):
        PENDING = 'PENDING', 'Pending'
        RUNNING = 'RUNNING', 'Running'
        SUCCESS = 'SUCCESS', 'Success'
        FAILED = 'FAILED', 'Failed'

    task = models.ForeignKey(
        AgentTask,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='executions'
    )
    agent = models.ForeignKey(
        Agent,
        on_delete=models.CASCADE,
        related_name='executions'
    )
    input = models.TextField()
    output = models.TextField(blank=True)
    execution_time = models.FloatField(
        null=True,
        blank=True,
        help_text="Execution time in seconds"
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING
    )
    tokens_used = models.IntegerField(default=0)
    started_at = models.DateTimeField(auto_now_add=True)
    finished_at = models.DateTimeField(null=True, blank=True)
    error_message = models.TextField(blank=True)

    def __str__(self):
        return f"Execution of {self.agent.name} for Task {self.task_id if self.task else 'None'} ({self.status})"


class AgentMemory(models.Model):
    agent = models.ForeignKey(Agent, on_delete=models.CASCADE, related_name='memories')
    memory_key = models.CharField(max_length=255)
    memory_value = models.TextField()
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Agent Memories"
        unique_together = ('agent', 'memory_key')

    def __str__(self):
        return f"Memory ({self.memory_key}) for {self.agent.name}"


class AgentContext(models.Model):
    agent = models.ForeignKey(Agent, on_delete=models.CASCADE, related_name='contexts')
    context_key = models.CharField(max_length=255)
    context_value = models.TextField()
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Agent Contexts"
        unique_together = ('agent', 'context_key')

    def __str__(self):
        return f"Context ({self.context_key}) for {self.agent.name}"


class AgentLog(models.Model):
    execution = models.ForeignKey(
        AgentExecution,
        on_delete=models.CASCADE,
        related_name='logs'
    )
    agent = models.ForeignKey(
        Agent,
        on_delete=models.CASCADE,
        related_name='logs'
    )
    level = models.CharField(max_length=20, default='INFO')
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"[{self.level}] {self.timestamp}: {self.message[:50]}"


class AgentConfiguration(models.Model):
    agent = models.ForeignKey(Agent, on_delete=models.CASCADE, related_name='configurations')
    config_key = models.CharField(max_length=255)
    config_value = models.TextField()
    is_secret = models.BooleanField(default=False)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('agent', 'config_key')

    def __str__(self):
        return f"Config ({self.config_key}) for {self.agent.name}"


# --- 10. MONITORING & INTELLIGENCE TELEMETRY MODELS ---

class SystemHealth(models.Model):
    overall_status = models.CharField(max_length=50, default='HEALTHY')
    cpu_usage = models.FloatField(default=0.0)
    memory_usage = models.FloatField(default=0.0)
    active_connections = models.IntegerField(default=0)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "System Health Records"

    def __str__(self):
        return f"System Health ({self.overall_status}) at {self.timestamp}"


class AgentHealth(models.Model):
    agent = models.ForeignKey(Agent, on_delete=models.CASCADE, related_name='health_stats')
    status = models.CharField(max_length=50, default='RUNNING')
    avg_response_time = models.FloatField(default=0.0)
    avg_execution_time = models.FloatField(default=0.0)
    error_count = models.IntegerField(default=0)
    retry_count = models.IntegerField(default=0)
    last_executed_at = models.DateTimeField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Agent Health Telemetry"

    def __str__(self):
        return f"Health: {self.agent.name} ({self.status})"


class DatabaseHealth(models.Model):
    connections_count = models.IntegerField(default=0)
    slow_queries_count = models.IntegerField(default=0)
    cache_hit_ratio = models.FloatField(default=100.0)
    table_sizes = models.JSONField(default=dict)
    index_usage_stats = models.JSONField(default=dict)
    migration_status = models.CharField(max_length=100, default='UP_TO_DATE')
    suggestions = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Database Health Records"

    def __str__(self):
        return f"DB Health at {self.timestamp} - Migrations: {self.migration_status}"


class StorageHealth(models.Model):
    bucket_name = models.CharField(max_length=150)
    storage_size_bytes = models.BigIntegerField(default=0)
    file_count = models.IntegerField(default=0)
    broken_urls_count = models.IntegerField(default=0)
    upload_failures_count = models.IntegerField(default=0)
    download_speed_kbps = models.FloatField(default=0.0)
    duplicate_files_count = models.IntegerField(default=0)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Storage Health Records"

    def __str__(self):
        return f"Storage: {self.bucket_name} - Size: {self.storage_size_bytes} Bytes"


class APIHealth(models.Model):
    endpoint = models.CharField(max_length=255)
    avg_response_time = models.FloatField(default=0.0)
    success_rate = models.FloatField(default=100.0)
    failure_rate = models.FloatField(default=0.0)
    auth_errors_count = models.IntegerField(default=0)
    validation_errors_count = models.IntegerField(default=0)
    traffic_count = models.IntegerField(default=0)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "API Health Records"

    def __str__(self):
        return f"API Route: {self.endpoint} - Traffic: {self.traffic_count}"


class StudentAnalytics(models.Model):
    student = models.ForeignKey('accounts.Student', on_delete=models.CASCADE, related_name='analytics')
    dashboard_load_time = models.FloatField(default=0.0)
    assignment_completion_rate = models.FloatField(default=0.0)
    ai_assignment_accuracy = models.FloatField(default=0.0)
    daily_usage_minutes = models.FloatField(default=0.0)
    activity_score = models.FloatField(default=100.0)
    experience_score = models.IntegerField(default=100) # 0-100 score
    weak_topics = models.JSONField(default=list)
    progress_status = models.CharField(
        max_length=50,
        choices=[('AT_RISK', 'At Risk'), ('ON_TRACK', 'On Track'), ('AHEAD', 'Ahead')],
        default='ON_TRACK'
    )
    personalized_recommendations = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Student Analytics Records"

    def __str__(self):
        return f"Analytics: {self.student.name} (Score: {self.experience_score})"


class CRAnalytics(models.Model):
    cr = models.ForeignKey('accounts.CR', on_delete=models.CASCADE, related_name='analytics')
    section = models.ForeignKey('academics.Section', on_delete=models.CASCADE, related_name='cr_analytics')
    pending_join_requests = models.IntegerField(default=0)
    daily_reviews_submitted = models.IntegerField(default=0)
    assignments_created = models.IntegerField(default=0)
    announcements_posted = models.IntegerField(default=0)
    avg_review_quality = models.FloatField(default=0.0)
    late_reviews_count = models.IntegerField(default=0)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "CR Analytics Records"

    def __str__(self):
        return f"CR Analytics: {self.cr} ({self.section.name})"


class AdminAnalytics(models.Model):
    college_growth_rate = models.FloatField(default=0.0)
    department_count = models.IntegerField(default=0)
    branch_count = models.IntegerField(default=0)
    section_count = models.IntegerField(default=0)
    semester_count = models.IntegerField(default=0)
    student_count = models.IntegerField(default=0)
    faculty_count = models.IntegerField(default=0)
    total_storage_used_bytes = models.BigIntegerField(default=0)
    total_api_calls = models.IntegerField(default=0)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Admin Analytics Records"

    def __str__(self):
        return f"Admin Growth Stats at {self.timestamp}"


class AIAnalytics(models.Model):
    questions_generated = models.IntegerField(default=0)
    revision_notes_generated = models.IntegerField(default=0)
    topics_processed = models.IntegerField(default=0)
    knowledge_base_size_bytes = models.BigIntegerField(default=0)
    embedding_count = models.IntegerField(default=0)
    ai_accuracy = models.FloatField(default=100.0)
    avg_generation_time = models.FloatField(default=0.0)
    prompt_performance_score = models.FloatField(default=100.0)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "AI Analytics Records"

    def __str__(self):
        return f"AI Stats: Knowledge Base {self.knowledge_base_size_bytes} Bytes"


class Alert(models.Model):
    class AlertType(models.TextChoices):
        SYSTEM = 'SYSTEM', 'System'
        DATABASE = 'DATABASE', 'Database'
        STORAGE = 'STORAGE', 'Storage'
        API = 'API', 'API'
        ACADEMIC = 'ACADEMIC', 'Academic'
        CR = 'CR', 'CR'

    class Severity(models.TextChoices):
        INFO = 'INFO', 'Info'
        WARNING = 'WARNING', 'Warning'
        CRITICAL = 'CRITICAL', 'Critical'

    title = models.CharField(max_length=200)
    message = models.TextField()
    alert_type = models.CharField(
        max_length=50,
        choices=AlertType.choices,
        default=AlertType.SYSTEM
    )
    severity = models.CharField(
        max_length=20,
        choices=Severity.choices,
        default=Severity.INFO
    )
    student = models.ForeignKey('accounts.Student', on_delete=models.CASCADE, null=True, blank=True, related_name='alerts')
    section = models.ForeignKey('academics.Section', on_delete=models.CASCADE, null=True, blank=True, related_name='alerts')
    is_resolved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"[{self.severity}] Alert: {self.title} ({self.alert_type})"


class Recommendation(models.Model):
    class Category(models.TextChoices):
        ACADEMIC = 'ACADEMIC', 'Academic'
        CR = 'CR', 'Class Representative'
        SYSTEM = 'SYSTEM', 'System'
        DATABASE = 'DATABASE', 'Database'

    title = models.CharField(max_length=200)
    message = models.TextField()
    category = models.CharField(
        max_length=50,
        choices=Category.choices,
        default=Category.ACADEMIC
    )
    student = models.ForeignKey('accounts.Student', on_delete=models.CASCADE, null=True, blank=True, related_name='recommendations')
    section = models.ForeignKey('academics.Section', on_delete=models.CASCADE, null=True, blank=True, related_name='recommendations')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"[{self.category}] Recommendation: {self.title}"


class AgentCapability(models.Model):
    agent = models.ForeignKey(Agent, on_delete=models.CASCADE, related_name='capabilities')
    capability_name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Agent Capabilities"
        unique_together = ('agent', 'capability_name')

    def __str__(self):
        return f"{self.agent.name}: {self.capability_name}"


class WorkflowStep(models.Model):
    class StepStatus(models.TextChoices):
        PENDING = 'PENDING', 'Pending'
        IN_PROGRESS = 'IN_PROGRESS', 'In Progress'
        COMPLETED = 'COMPLETED', 'Completed'
        FAILED = 'FAILED', 'Failed'
        SKIPPED = 'SKIPPED', 'Skipped'
        AWAITING_APPROVAL = 'AWAITING_APPROVAL', 'Awaiting Approval'

    workflow = models.ForeignKey(AgentWorkflow, on_delete=models.CASCADE, related_name='steps_list')
    step_number = models.IntegerField(default=1)
    name = models.CharField(max_length=150)
    agent = models.ForeignKey(Agent, on_delete=models.SET_NULL, null=True, blank=True, related_name='steps')
    input_mapping = models.JSONField(default=dict, help_text="Maps previous outputs to inputs")
    status = models.CharField(max_length=30, choices=StepStatus.choices, default=StepStatus.PENDING)
    depends_on_steps = models.JSONField(default=list, help_text="List of step numbers this step depends on")
    retry_count = models.IntegerField(default=0)
    max_retries = models.IntegerField(default=3)
    timeout_seconds = models.IntegerField(default=60)
    is_critical = models.BooleanField(default=True, help_text="If true, step failure fails the entire workflow")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['step_number']
        unique_together = ('workflow', 'step_number')

    def __str__(self):
        return f"{self.workflow.name} - Step {self.step_number}: {self.name}"


class TaskDependency(models.Model):
    task = models.ForeignKey(AgentTask, on_delete=models.CASCADE, related_name='dependencies')
    depends_on = models.ForeignKey(AgentTask, on_delete=models.CASCADE, related_name='dependent_tasks')

    class Meta:
        verbose_name_plural = "Task Dependencies"
        unique_together = ('task', 'depends_on')

    def __str__(self):
        return f"{self.task.title} depends on {self.depends_on.title}"


class TaskResult(models.Model):
    task = models.OneToOneField(AgentTask, on_delete=models.CASCADE, related_name='result')
    output_data = models.TextField(blank=True)
    execution_time = models.FloatField(default=0.0)
    tokens_used = models.IntegerField(default=0)
    status = models.CharField(max_length=50, default='SUCCESS')
    error_message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Result for {self.task.title} ({self.status})"


class AgentExecutionLog(models.Model):
    execution = models.ForeignKey(AgentExecution, on_delete=models.CASCADE, related_name='execution_logs')
    level = models.CharField(max_length=20, default='INFO')
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"[{self.level}] {self.timestamp}: {self.message[:50]}"


class AgentMetric(models.Model):
    agent = models.ForeignKey(Agent, on_delete=models.CASCADE, related_name='metrics')
    metric_key = models.CharField(max_length=255)
    metric_value = models.FloatField(default=0.0)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Metric: {self.agent.name} - {self.metric_key}: {self.metric_value}"

