# Contributing Guidelines

Thank you for contributing to QISHub! To ensure a smooth development workflow, please adhere to the guidelines outlined below.

---

## 1. Setup Instructions

1. **Clone the Repository**:
   ```bash
   git clone <repository_url>
   cd qishub-backend
   ```

2. **Initialize Virtual Environment**:
   - **Windows**:
     ```bash
     python -m venv .venv
     .venv\Scripts\activate
     ```
   - **Linux/macOS**:
     ```bash
     python3 -m venv .venv
     source .venv/bin/activate
     ```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment Variables**:
   Create a `.env` file in the root directory (based on `.env.example` configurations):
   ```ini
   DB_NAME=postgres
   DB_USER=postgres
   DB_PASSWORD=your_password
   DB_HOST=localhost
   DB_PORT=5432
   GEMINI_API_KEY=your_key
   ```

5. **Run Migrations & Local Server**:
   ```bash
   python manage.py migrate
   python manage.py runserver
   ```

---

## 2. Development Guidelines

### Coding Style
- Follow **PEP 8** style guidelines for Python code.
- Write descriptive class, method, and variable names.
- Keep business logic in `services.py` and reuse validations inside `validators.py`. Views must only handle serializers validation and client routing.

### Branch Naming Conventions
- Feature tasks: `feature/short-description`
- Bug fixes: `bugfix/short-description`
- Telemetry/Chore: `chore/short-description`

### Commit Message Guidelines
Use structured commit prefixes:
- `feat: <description>` (new feature implementations)
- `fix: <description>` (bug resolution)
- `docs: <description>` (documentation edits)
- `test: <description>` (test suites modifications)
- `chore: <description>` (config adjustments)

Example:
```bash
git commit -m "feat: implement daily class review CR endpoint and progress metrics"
```
