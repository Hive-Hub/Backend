# QISHub Backend

## Overview
QISHub is an enterprise-grade Academic Operating System designed to simplify coordination between students, Class Representatives (CRs), and university faculty. By incorporating a robust AI Multi-Agent system (AgentOS) alongside comprehensive Student and CR REST APIs, QISHub manages course plan tracking, daily class progress reporting, and automated study questions generation from classroom lectures.

---

## Features
- **Role-Based Profiles**: Structured roles for `STUDENT`, `CR`, and `ADMIN`.
- **Student Portal**: Dashboard views, profile management, timetable entries, alerts, reports, resources search, and assignment submissions.
- **CR Operations**: Pending join requests approvals, class reviews covers log, resource uploads, assignment postings, and AI questions triggers.
- **Timetable & Daily Reviews**: Automatic syllabus progress tracking based on topics checked off during lectures.
- **Resources Library**: Asset storage integrated with Supabase Storage buckets.
- **AgentOS Framework**: LLM executor orchestration, parallel workflow engines, capability tagging, and system-wide telemetry monitoring.

---

## Tech Stack
- **Framework**: Django 6.0.6 & Django REST Framework (DRF) 3.17.1
- **Database**: Supabase PostgreSQL
- **Storage Service**: Supabase Cloud S3 bucket storage via `boto3` interface
- **Telemetry System**: `psutil` CPU/Memory auditor
- **AI Engine**: Google GenAI SDK (Gemini client integration)

---

## Architecture
```text
  User Client Request
         ↓
    REST API View
         ↓
   Service Logic
         ↓
  PostgreSQL DB  ←---  AgentOS Framework  ---→  Supabase Storage
```
For more information, refer to [BACKEND_ARCHITECTURE.md](file:///c:/projects/qishub-backend/BACKEND_ARCHITECTURE.md).

---

## Folder Structure
A simplified layout of the backend application:
```text
qishub-backend/
├── academics/       # Departments, semesters, timetables, and review logs
├── accounts/        # User roles, student/CR profiles, and session handling
├── agents/          # AgentOS multi-agent orchestrator and engine scripts
├── announcements/   # Notices and announcements listings
├── assignments/     # Homework tasks, answers submissions, and quiz banks
├── colleges/        # College registration schemas
├── config/          # Django project settings and base routing
├── resources/       # File library resource registries
└── manage.py        # Django CLI entrypoint
```
The complete folder architecture is automatically mapped in [DIRECTORY_TREE.md](file:///c:/projects/qishub-backend/DIRECTORY_TREE.md).

---

## Installation

### 1. Create Virtual Environment
- **Windows**:
  ```bash
  python -m venv .venv
  ```
- **Linux/macOS**:
  ```bash
  python3 -m venv .venv
  ```

### 2. Activate Virtual Environment
- **Windows**:
  ```bash
  .venv\Scripts\activate
  ```
- **Linux/macOS**:
  ```bash
  source .venv/bin/activate
  ```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

---

## Database & Local Setup

1. **Environment Configuration**:
   Create a `.env` file in the root folder using `.env.example` configurations. Make sure credentials map to your Supabase PostgreSQL database:
   ```ini
   DB_NAME=postgres
   DB_USER=postgres
   DB_PASSWORD=your_password
   DB_HOST=your_supabase_endpoint
   DB_PORT=5432
   GEMINI_API_KEY=your_key
   ```

2. **Apply Migrations**:
   ```bash
   python manage.py migrate
   ```

3. **Initialize Default Agents**:
   Pre-populate the database with standard AgentOS worker settings and capability tags:
   ```bash
   python manage.py run_monitoring_jobs --job scheduler
   ```

4. **Create Admin User**:
   ```bash
   python manage.py createsuperuser
   ```

5. **Start Local Server**:
   ```bash
   python manage.py runserver
   ```

---

## Running on Replit
To deploy and test QISHub Backend directly on Replit:
1. Import this repository into a new Repl.
2. Select **Python** as the primary workspace environment.
3. Configure the environment variables (`DB_NAME`, `DB_USER`, etc.) inside Replit's **Secrets (Environment Variables)** panel.
4. Run setup commands in the terminal:
   ```bash
   python manage.py migrate
   python manage.py runserver 0.0.0.0:8000
   ```

---

## API & Agent Documentation
- **Master REST API Reference**: [api_list.txt](file:///c:/projects/qishub-backend/api_list.txt) (contains complete endpoints payload structures, examples, and rules).
- **OpenAPI Schema**: [swagger_docs.yaml](file:///c:/projects/qishub-backend/swagger_docs.yaml).
- **AgentOS Architectural Design**: [AGENTS.md](file:///c:/projects/qishub-backend/AGENTS.md) (contains agent lists, responsibilities, and worker isolation rules).
- **Vision Document**: [PROJECT_INFO.md](file:///c:/projects/qishub-backend/PROJECT_INFO.md).

---

## Roadmap
- **SAML Single Sign-On**: Unified enterprise authentication.
- **Interactive AI Tutor**: Student questions helper chat agent.
- **Offline Sync**: Local SQL Sync support in Flutter applications.
- **Facial Timetable Attendance**: Class camera attendance checks.
- **Multi-Tenant SaaS Scaling**: Deployable instances for multiple colleges.

---

## License
Licensed under the [MIT License](file:///c:/projects/qishub-backend/LICENSE).
