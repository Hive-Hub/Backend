# Project Vision & Specifications

## 1. Project Vision
QISHub is an enterprise-grade Academic Operating System designed to streamline collaboration between Students, Class Representatives (CRs), and Faculty. By leveraging AI Multi-Agent workflows, QISHub monitors student performance index rates, automates curriculum mapping validations, and generates customized learning reinforcement questions directly derived from lectures and reviews.

---

## 2. Architecture Overview
QISHub uses a decoupled, modular design divided into three primary tiers:
- **Presentation Tier**: REST APIs (Django REST Framework) providing role-filtered access controls.
- **Service & Intelligence Layer**: Extensible domain services wrapping business transactions, integrated with the AgentOS Multi-Agent system (Orchestrator, Project Manager, and specialized Workers).
- **Persistence & Cloud Storage**: Supabase PostgreSQL database holding normalization schemas and Supabase S3 bucket storages mapping uploaded student materials.

---

## 3. Database Design & Schema Normalization
The database utilizes a PostgreSQL database structure, ensuring referential integrity and performance:
- **Accounts Domain**: Models custom user profiles mapping role permissions (`STUDENT`, `CR`, `ADMIN`), student registrar fields, CR assignments, and semester progress indices.
- **Academics Domain**: Maintains academic structures (Departments, Branches, Sections, Semesters, Subjects catalog, unit chapters, sub-topic tables, and student daily reviews covers). Timetable entries map lectures.
- **Assignments & Question Banks**: Connects standard homework and AI-generated quiz models.
- **Resources**: Records file metadata (`StoredFile`) and links files to corresponding subject resource catalog libraries.

---

## 4. Development Phases
1. **Phase 1: Basic Scaffolding & Models**: Custom User profiles setup and core Academics catalog configuration.
2. **Phase 2: Mappings & Timetables**: Dynamic timetables creation and CR assignment hierarchies.
3. **Phase 3: AgentOS Engine**: Orchestrator, PM, and worker executors, multi-provider LLM integrations, and sequential/parallel scheduler routines.
4. **Phase 4: Exposing REST views**: Standardized API endpoints (auth, dashboard, schedules, reviews, uploads, progress logs) wrapping data envelopes.
5. **Phase 5: Mobile & Frontend Integration**: Angular web portal and Flutter mobile application deployment.
6. **Phase 6: Multi-College SaaS Scaling**: Supporting multi-tenant college environments.
