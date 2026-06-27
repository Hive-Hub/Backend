# Project Directory Tree

```text
qishub-backend/
├── AGENTS.md
├── BACKEND_ARCHITECTURE.md
├── CHANGELOG.md
├── CODE_OF_CONDUCT.md
├── CONTRIBUTING.md
├── LICENSE
├── PROJECT_INFO.md
├── academics
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── migrations
│   │   ├── 0001_initial.py
│   │   ├── 0002_semester_status_alter_semester_department_branch_and_more.py
│   │   ├── 0003_dailyclassreview_semestersubject_and_more.py
│   │   ├── 0004_facultyassignment_semestercalendar_semesterplan_and_more.py
│   │   ├── 0005_facultyassignment_faculty_and_more.py
│   │   ├── 0006_sectionsemester_timetable_timetableentry.py
│   │   ├── 0007_dailyclassreview_timetable_entry_attendance.py
│   │   └── __init__.py
│   ├── models.py
│   ├── permissions.py
│   ├── serializers.py
│   ├── services.py
│   ├── signals.py
│   ├── tests.py
│   ├── urls.py
│   ├── validators.py
│   └── views.py
├── accounts
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── management
│   │   └── commands
│   │       └── seed_demo_data.py
│   ├── migrations
│   │   ├── 0001_initial.py
│   │   ├── 0002_student_branch_student_section_and_more.py
│   │   ├── 0003_data_migration.py
│   │   ├── 0004_semesterprogress_semesterreport_subjectprogress.py
│   │   ├── 0005_faculty.py
│   │   └── __init__.py
│   ├── models.py
│   ├── pagination.py
│   ├── permissions.py
│   ├── serializers.py
│   ├── services.py
│   ├── signals.py
│   ├── tests.py
│   ├── urls.py
│   ├── utils.py
│   ├── validators.py
│   └── views.py
├── agents
│   ├── __init__.py
│   ├── adapters
│   │   ├── __init__.py
│   │   └── llm_adapter.py
│   ├── admin.py
│   ├── apps.py
│   ├── executors
│   │   ├── __init__.py
│   │   ├── base.py
│   │   └── llm_executor.py
│   ├── health.py
│   ├── management
│   │   └── commands
│   │       └── run_monitoring_jobs.py
│   ├── manager.py
│   ├── managers
│   │   ├── __init__.py
│   │   └── agent_manager.py
│   ├── metrics.py
│   ├── migrations
│   │   ├── 0001_initial.py
│   │   ├── 0002_adminanalytics_aianalytics_apihealth_databasehealth_and_more.py
│   │   ├── 0003_agenttask_approval_required_agenttask_is_approved_and_more.py
│   │   └── __init__.py
│   ├── models.py
│   ├── orchestrator.py
│   ├── permissions.py
│   ├── prompts
│   │   ├── ai_learning.md
│   │   ├── authentication.md
│   │   ├── backend.md
│   │   ├── contexts
│   │   │   ├── api_rules.md
│   │   │   ├── architecture.md
│   │   │   ├── coding_rules.md
│   │   │   ├── database.md
│   │   │   ├── django_rules.md
│   │   │   ├── security_rules.md
│   │   │   └── supabase_rules.md
│   │   ├── database.md
│   │   ├── documentation.md
│   │   ├── manager.md
│   │   ├── monitoring.md
│   │   ├── review.md
│   │   ├── storage.md
│   │   └── testing.md
│   ├── providers
│   │   ├── __init__.py
│   │   ├── azure_provider.py
│   │   ├── base_provider.py
│   │   ├── claude_provider.py
│   │   ├── gemini_provider.py
│   │   ├── local_provider.py
│   │   └── openai_provider.py
│   ├── registry.py
│   ├── scheduler.py
│   ├── serializers.py
│   ├── services
│   │   ├── __init__.py
│   │   ├── api_service.py
│   │   ├── database_service.py
│   │   ├── monitoring_service.py
│   │   ├── review_service.py
│   │   ├── storage_service.py
│   │   ├── testing_service.py
│   │   └── workflow_service.py
│   ├── templates
│   ├── tests
│   │   ├── __init__.py
│   │   ├── test_telemetry.py
│   │   └── test_workflow_engine.py
│   ├── urls.py
│   ├── utils
│   │   ├── __init__.py
│   │   └── llm_client.py
│   ├── views.py
│   ├── workflow_engine.py
│   └── workflows
│       ├── __init__.py
│       └── engine.py
├── announcements
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── migrations
│   │   ├── 0001_initial.py
│   │   ├── 0002_announcement_semester.py
│   │   └── __init__.py
│   ├── models.py
│   ├── permissions.py
│   ├── serializers.py
│   ├── services.py
│   ├── tests.py
│   ├── urls.py
│   ├── validators.py
│   └── views.py
├── api_list.txt
├── assignments
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── migrations
│   │   ├── 0001_initial.py
│   │   ├── 0002_assignment_assignment_type_assignment_difficulty_and_more.py
│   │   └── __init__.py
│   ├── models.py
│   ├── permissions.py
│   ├── serializers.py
│   ├── services.py
│   ├── tests.py
│   ├── urls.py
│   ├── validators.py
│   └── views.py
├── colleges
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── migrations
│   │   ├── 0001_initial.py
│   │   └── __init__.py
│   ├── models.py
│   ├── tests.py
│   └── views.py
├── config
│   ├── __init__.py
│   ├── ai_utils.py
│   ├── asgi.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── db.sqlite3
├── grnimaiApi.txt
├── manage.py
├── requirements.txt
├── resources
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── migrations
│   │   ├── 0001_initial.py
│   │   ├── 0002_storedfile_resourcelibrary.py
│   │   └── __init__.py
│   ├── models.py
│   ├── permissions.py
│   ├── serializers.py
│   ├── services.py
│   ├── tests.py
│   ├── urls.py
│   ├── validators.py
│   └── views.py
├── storagesuperbase.txt
└── swagger_docs.yaml
```
