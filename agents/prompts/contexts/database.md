# Database Schema Context

- **PostgreSQL**: Supabase PostgreSQL is the primary store.
- **Conventions**: Standard foreign keys, proper cascading or SET_NULL policies, unique constraints, and indexes on frequently searched attributes.
- **No changes to existing models**: All modifications to other schemas are prohibited. Only extend models inside the `agents` application.
