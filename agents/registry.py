import logging
from .models import Agent, AgentWorkflow, AgentPrompt, AgentCapability, AgentConfiguration
from .executors.llm_executor import LLMExecutor

logger = logging.getLogger(__name__)

class AgentRegistry:
    """
    Agent Registry handles registering agents, loading default configurations/prompts,
    registering default workflows, and capability discovery.
    """
    
    @classmethod
    def get_executor(cls, agent):
        return LLMExecutor(agent)

    @classmethod
    def get_agent_by_slug(cls, slug):
        return Agent.objects.filter(slug=slug, is_active=True).first()

    @classmethod
    def get_workflow_by_name(cls, name):
        return AgentWorkflow.objects.filter(name=name, active=True).first()

    @classmethod
    def discover_capabilities(cls, query_keyword: str):
        """
        Capability Discovery: Finds active agents with capabilities matching the query keyword.
        """
        return Agent.objects.filter(
            is_active=True,
            capabilities__capability_name__icontains=query_keyword
        ).distinct()

    @classmethod
    def setup_defaults(cls):
        """
        Pre-populates the database with the 11 standard agents, their prompts, configurations, and default workflow.
        """
        agents_data = [
            {
                "name": "Orchestrator Agent",
                "slug": "orchestrator",
                "agent_type": Agent.AgentType.ORCHESTRATOR,
                "description": "Responsible for request parsing, query intent analysis, and dynamic workflow generation.",
                "capabilities": ["orchestration", "decomposition", "planning", "parsing"]
            },
            {
                "name": "Project Manager Agent",
                "slug": "project-manager",
                "agent_type": Agent.AgentType.PROJECT_MANAGER,
                "description": "Responsible for task planning, distribution, tracking, and conflict detection.",
                "capabilities": ["project coordination", "aggregation", "task tracking", "coordination"]
            },
            {
                "name": "Database Architect Agent",
                "slug": "database-architect",
                "agent_type": Agent.AgentType.DATABASE_ARCHITECT,
                "description": "Designs database models, relationships, migrations, constraints, and indexes.",
                "capabilities": ["models", "migrations", "indexes", "constraints", "relationships"]
            },
            {
                "name": "Backend API Agent",
                "slug": "backend-api",
                "agent_type": Agent.AgentType.BACKEND_API,
                "description": "Builds Django REST APIs, ViewSets, Serializers, Validation, and permissions.",
                "capabilities": ["views", "serializers", "urls", "permissions", "business logic"]
            },
            {
                "name": "Authentication Agent",
                "slug": "authentication",
                "agent_type": Agent.AgentType.AUTHENTICATION,
                "description": "Secures applications with JWT, roles checks, and granular permissions validation.",
                "capabilities": ["jwt", "role filters", "session safety", "auth token"]
            },
            {
                "name": "Storage Agent",
                "slug": "storage",
                "agent_type": Agent.AgentType.STORAGE,
                "description": "Manages file uploads (PDFs, Images), signed URLs, and asset versioning using Supabase Storage.",
                "capabilities": ["supabase storage", "bucket uploads", "download speed", "file cleanup"]
            },
            {
                "name": "AI Learning Agent",
                "slug": "ai-learning",
                "agent_type": Agent.AgentType.AI_LEARNING,
                "description": "Extracts daily review topics, generates questions, constructs semester plans and timetables.",
                "capabilities": ["daily reviews", "questions", "topics", "semester calendar", "timetable parsing"]
            },
            {
                "name": "Testing Agent",
                "slug": "testing",
                "agent_type": Agent.AgentType.TESTING,
                "description": "Generates unit tests, API tests, migration tests, and performs performance validations.",
                "capabilities": ["unit tests", "integration tests", "mock requests", "load testing"]
            },
            {
                "name": "Documentation Agent",
                "slug": "documentation",
                "agent_type": Agent.AgentType.DOCUMENTATION,
                "description": "Creates system documentation, README guides, API specifications, and Swagger setup configs.",
                "capabilities": ["swagger", "openapi", "readme", "architecture logs", "developer documentation"]
            },
            {
                "name": "Review Agent",
                "slug": "review",
                "agent_type": Agent.AgentType.REVIEW,
                "description": "Conducts security scans, best practices checks, and identifies duplicate implementations.",
                "capabilities": ["security check", "code duplication", "lint standards", "code quality review"]
            },
            {
                "name": "Monitoring & Intelligence Agent",
                "slug": "monitoring-intelligence",
                "agent_type": Agent.AgentType.MONITORING,
                "description": "Continuously monitors health, compiles system analytics, and generates recommendations/predictions.",
                "capabilities": ["slow queries", "system health", "latency check", "storage count", "experience score"]
            }
        ]

        created_agents = []
        for a_data in agents_data:
            agent, created = Agent.objects.get_or_create(
                slug=a_data["slug"],
                defaults={
                    "name": a_data["name"],
                    "agent_type": a_data["agent_type"],
                    "description": a_data["description"],
                    "is_active": True
                }
            )
            created_agents.append(agent)
            
            # Setup capabilities
            for cap_name in a_data["capabilities"]:
                AgentCapability.objects.get_or_create(
                    agent=agent,
                    capability_name=cap_name
                )
            
            # Setup configs
            AgentConfiguration.objects.get_or_create(
                agent=agent,
                config_key="llm_provider",
                defaults={"config_value": "gemini", "is_secret": False}
            )
            AgentConfiguration.objects.get_or_create(
                agent=agent,
                config_key="llm_model",
                defaults={"config_value": "gemini-2.5-flash", "is_secret": False}
            )
            
            # Setup prompt placeholder if it doesn't exist
            if not AgentPrompt.objects.filter(agent=agent).exists():
                AgentPrompt.objects.create(
                    agent=agent,
                    system_prompt=f"You are the {a_data['name']}. Undergo your responsibilities: {a_data['description']}",
                    developer_prompt="Adhere to PEP8 rules and standard Django designs.",
                    user_template="Task: {task_title}\nDescription: {task_description}\nContext: {input_data}"
                )

        # Setup Default Workflow
        workflow_steps = [
            {"step_number": 1, "agent_slug": "project-manager", "description": "Deconstruct request and prepare execution plan"},
            {"step_number": 2, "agent_slug": "database-architect", "description": "Review model schemas, relations, and index choices"},
            {"step_number": 3, "agent_slug": "backend-api", "description": "Draft standard Django REST Views, URLs, and Serializers"},
            {"step_number": 4, "agent_slug": "testing", "description": "Formulate unit tests, model assertions, and mock API tests"},
            {"step_number": 5, "agent_slug": "review", "description": "Verify code constraints, query counts, and security checks"},
            {"step_number": 6, "agent_slug": "documentation", "description": "Generate OpenAPI specs, Swagger summaries, and architectural logs"}
        ]

        AgentWorkflow.objects.get_or_create(
            name="Developer Workflow",
            defaults={
                "description": "Coordinated developer execution flow from Project Manager to Documentation Agent",
                "steps": workflow_steps,
                "active": True
            }
        )

        return created_agents
