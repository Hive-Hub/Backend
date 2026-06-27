# Backend Architecture Spec

This document details the internal design patterns, structural boundaries, and request pathways of the QISHub Backend.

---

## 1. Request Flow (Standard Pattern)

Every HTTP request traverses the following lifecycle:

```text
  Client Request
       ↓
  Django Middleware (CORS, Security)
       ↓
  DRF URL Router Match
       ↓
  Authentication Check (JWTAuthentication token decode)
       ↓
  Permission Guards (IsStudent, IsCR checking user role)
       ↓
  Serializer Validation (Parses payloads & formats errors)
       ↓
  Validators.py Constraints (Complex business logic bounds)
       ↓
  Service Layer Call (Delegate to accounts/academics/etc services)
       ↓
  Database Transaction (Atomic saves/updates)
       ↓
  Standard Envelope Response (Formats success/error structure)
```

---

## 2. Authentication Flow (Signed Bearer Token)

Rather than maintaining server-side state or DB tables for JWTs, QISHub uses a cryptographic signature design:

```text
  [Login Endpoint] -> Verify Email/Password -> Generate Signed Payload (ID, Email, Role)
                                                        ↓
                                         Return token string to client
                                                        ↓
  [Subsequent Request] -> Extract Bearer Token -> Decrypt and verify HMAC signature
                                                        ↓
                                    Validate timestamp and fetch user from DB
```

---

## 3. Storage Pipeline (Multipart Resource Uploads)

File uploads bypass traditional local disk storage, streaming directly to Supabase Storage:

1. **Client Submission**: Uploads a resource using `multipart/form-data`.
2. **File Validation**: `resources/validators.py` checks constraints (allowed extensions like PDF, PPT, ZIP).
3. **Storage Client**: `StorageService` streams raw bytes to the S3 bucket via boto3 interface.
4. **Database Registration**:
   - Creates a `StoredFile` capturing S3 URL and size.
   - Registers a `ResourceLibrary` mapping to the selected course catalog and semester.
   - Back-populates legacy `Resource` record for backward compatibility.

---

## 4. AI Question Generation Pipeline

Automated quiz generation is linked to daily class reviews:

1. **Review Submission**: CR submits a daily review specifying topics covered.
2. **Question Generation Call**: CR triggers `/api/cr/generate-questions/` supplying `review_id`.
3. **Agent Activation**: The Testing/AI Agent retrieves topics syllabus text and formats an LLM prompt.
4. **LLM Execution**: The `LLMAdapter` makes a call to Gemini (or another configured provider).
5. **DB Insertion**: The generated JSON questions are parsed, creating an `Assignment` (type `AI_GENERATED`) and populate the `QuestionBank` table.
