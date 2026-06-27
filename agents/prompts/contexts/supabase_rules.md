# Supabase Rules Context

- **Supabase Storage**: Interfaced through Django Storages S3-compatible backend.
- **RLS**: Row-Level Security settings must be respected. Use signed URLs for sensitive files.
- **Connection pooling**: Ensure queries are fast and do not leak connections.
