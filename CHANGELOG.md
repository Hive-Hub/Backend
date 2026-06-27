# Changelog

All notable changes to the QISHub Backend project will be documented in this file.

---

## [0.5.0] - 2026-06-27
### Added
- Completed Student & Class Representative REST APIs under `/api/` routing namespace.
- Designed lightweight cryptographic signed token authentication (HMAC-SHA256, 24h expiration) under `accounts.permissions.JWTAuthentication`.
- Created custom exception handler wrapping validation / system exceptions into standard format envelopes.
- Created `api_list.txt` master endpoints documentation and `swagger_docs.yaml` OpenAPI 3.0 specification.
- Exposed automated unit test coverage inside each application testing module.

---

## [0.4.0] - 2026-06-27
### Added
- Designed the AgentOS multi-agent system structure.
- Implemented Orchestrator, Project Manager, and Worker executors.
- Added multi-provider adapters (`Gemini`, `OpenAI`, `Claude`, `Azure`, and local `Ollama/LM Studio`).
- Integrated sequential and parallel workflow engines supporting step timeouts, skips, and retries.
- Added the Monitoring and Intelligence Agent layer conducting telemetry audits (health performance, connection leaks, student experience scores).

---

## [0.3.0] - 2026-06-25
### Added
- Integrated Class Representative (CR) assignments system.
- Implemented Section semesters, timetable structures, and resources libraries.
- Added support for Daily Class Reviews representing topic coverage source of truth.

---

## [0.2.0] - 2026-06-20
### Added
- Built structural layout of Academics model hierarchies (Departments, Branches, Sections, Semesters, and Subjects).
- Setup Django admin lists and search filters.

---

## [0.1.0] - 2026-06-15
### Added
- Core backend initialization using Django 6.
- Custom User authentication model support.
- Colleges and basic accounts profile definitions.
