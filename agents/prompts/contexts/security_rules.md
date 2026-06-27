# Security & Access Control Context

- **Roles & Hierarchy**: Admin is superuser with write access. CR has read-only access. Student has no access.
- **Data isolation**: Ensure users can only query information that matches their permission scope.
- **Credentials safety**: Never hardcode API keys or secrets. Store them in configurations or environment variables.
