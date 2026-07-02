# AI Campus OS Backend — Spec Understanding & Gap Analysis

My complete reading of **"AI Campus OS – Backend Development Requirements"** + the SRS volumes
(Vol 1 Authentication, Vol 2 Student) + the **Student/Parent Mobile App API Requirements**, mapped
against what currently exists in this repo. This is the source of truth to align on before building.

> Framework note: the SRS volume headers say *"FastAPI, SQLAlchemy, Alembic"*, but the primary
> Requirements doc and every deliverable say **Django 5.x + DRF**. Treating the FastAPI line as a
> template copy-paste artifact → **stack stays Django + DRF**. (Flag if that's wrong — it'd be a rewrite.)

---

## A. What the system is
- **Multi-tenant SaaS College ERP.** Many colleges share one deployment; **complete data isolation by `college_id`**; no cross-college leakage.
- **Clients:** Flutter mobile apps (Student, Parent, Faculty) + React Admin Portal. (The Expo/React-Native app in `../education-os` is our working stand-in for the mobile client.)
- **7 roles:** Super Admin, **College Admin**, Principal, HOD, Faculty, Student, Parent.
- Enterprise-grade: modular, scalable, secure, maintainable, documented, tested (≥80%).

## B. Cross-cutting standards
| Concern | Spec says | Repo today | Gap |
| --- | --- | --- | --- |
| **Response envelope** | success `{"status":"success","message","data"}` · error `{"status":"error","message","errors":[]}` | `{"success": bool, message, data, errors, meta}` | **field is `status` (string), not `success` (bool)** |
| **Field casing** | examples are **snake_case** (`roll_no`, `attendance_percentage`, `pending_fees`) | camelCase | **decide: snake_case + app maps, or keep camel** |
| Pagination / filter / search / sort | required on list APIs (`?page=&limit=&…`) | pagination yes; filter/search/order partial | align (note: spec uses `limit`, I used `page_size`) |
| HTTP status codes | 200/201/400/401/403/404/409/422/500 | mostly | add 409/422 usage |
| Security | CSRF, CORS, SQLi/XSS, **rate limiting/throttling**, HTTPS, secure cookies/headers, OWASP | CORS yes; throttling configured; headers partial | add throttle scopes, secure headers |
| **Caching** | Redis, keys `student:{user_id}` `dashboard:{user_id}` `attendance:{user_id}` `fees:{user_id}` `notifications:{user_id}`, **TTL 30 min**, invalidate→reload→restore on write | Redis wired; keys/TTL differ (300s, `student_dashboard_{id}`) | rename keys + TTL 1800s + wire invalidation everywhere |
| **Audit logs** | user, module, action(CREATE/UPDATE/DELETE/LOGIN/LOGOUT/ROLE/PASSWORD), **previous_value, current_value (JSONB)**, ip, device, timestamp | AuditLog has actor/action/entity/entity_id/changes/ip | **add previous_value/current_value/module/device**; wire login/logout/role/password |
| Background tasks (Celery) | email, SMS, push, attendance summary, daily/weekly reports, AI reports, scheduled notifications, certificate generation | Celery wired; task stubs partial | implement the listed tasks |
| Swagger | per-API summary/description/auth/req/resp/errors/sample/codes at **`/api/schema/swagger-ui/`** & **`/redoc/`** | drf-spectacular at `/api/docs/` | add swagger-ui/redoc paths; enrich schema |
| File uploads | S3, store **URL only** (profile img, docs, certificates, hall tickets, assignments) | storages/boto3 configured; not wired to models | add file fields/URLs |
| Logging | structured; login/logout/errors/validation/exceptions/perf/tasks | Django default | add structured logging config |
| Testing | unit/API/serializer/permission/auth, **≥80% coverage** | thin per-module tests | expand |
| Coding standards | PEP8, SOLID, **Repository + Service Layer**, DI, type hints, docstrings, no logic in views | Repository+Service layers present ✓ | keep |

## C. Data-model foundation (every table)
Spec mandates on **every** table: `id (UUID)`, **`college_id (UUID)`**, `created_at`, `updated_at`,
`created_by`, `updated_by`, **`is_active`**, `is_deleted`. Plus UUID PKs, FK constraints, proper +
composite indexes, soft delete.
- **Repo `BaseModel` today:** `id, created_at, updated_at, created_by, updated_by, is_deleted, deleted_at`.
- **Gaps:** ❌ **`college_id` (multi-tenancy) — missing on every model** · ❌ `is_active` · tenant-scoped
  managers/middleware to enforce isolation.

## D. Authentication & User Management (SRS Vol 1) — required
- **Tokens:** JWT access **30 min**, refresh **7 days**, **rotation**, **revocation**. ✓ (config close; verify rotation+blacklist)
- **Password:** BCrypt/PBKDF2 (Django hasher ok); **policy**: 8–32 chars, upper/lower/digit/special, not contain username, **last-5 history**, **90-day expiry**. ❌ not implemented.
- **Login identifiers:** username **or** email **or** phone. ❌ (email only today).
- **Single active login:** new-device login must invalidate previous session, revoke previous JWT, remove Redis session, force-logout previous device. ❌
- **Account locking:** 5 failed attempts → lock 30 min. ❌
- **Email verification + OTP (email/SMS).** ⚠️ OTP model exists; verification/SMS not wired.
- **Login history + audit logs.** ❌ login_history missing.
- **RBAC via DB tables** — spec defines tables `roles`, `permissions`, `role_permissions`, and per-endpoint permission checks. Repo uses a **role enum on User + code-level matrix** (no permissions tables). Gap: DB-driven permissions.
- **Required tables (SRS §7):** `users` (username, email, phone, password_hash, role_id, is_active, failed_login_attempts, account_locked, last_login…), `roles`, `permissions`, `role_permissions`, `user_sessions` (access/refresh/device/ip/browser/os/login_time/last_activity/is_active), `login_history`, `audit_logs` (previous_value/current_value JSONB/ip). Repo has a custom `User` + `OTP` only.
- **Role naming:** spec **"College Admin"**; repo uses `admin`.
- **Login flow (SRS §8):** validate user → bcrypt → fail-count/lock → check user active → **check college active** → check existing session (single-login) → issue JWT+refresh → **store session in PG + Redis** → login history → response.

## E. Student module (SRS Vol 2) — required tables & APIs
- **Tables:** `students` (student_id, college_id, user_id, admission_no, register_no, roll_no, first/last_name, gender ENUM, dob, blood_group, phone, email, degree_id, department_id, course_id, semester, section, joining_year, graduation_year, status ENUM, timestamps); `student_profile` (father/mother/guardian, address/city/district/state/country/pincode/nationality/emergency_contact); `student_medical`; `student_documents` (document_type, file_name, file_url).
- Repo `students` app is close but: no `register_no`, no `degree_id/course_id` split the same way, profile/medical/documents partial, **no college_id**.
- **APIs (SRS §5):** `POST /api/v1/students`, `GET /api/v1/students/{user_id}`, `PUT /api/v1/students/{student_id}`, `DELETE` (**soft delete** → status INACTIVE + is_deleted + deleted_at), `GET /api/v1/students` (search: admission/roll/name/dept/sem/section/year/status + pagination/sort/filter). Validation + 12-step business logic + Redis cache (`student:{id}`, TTL 30m) + audit on every op.

## F. Mobile App API contract (authoritative endpoints) — **major mismatch with repo**
Spec paths are **`{user_id}`-parameterized**; repo built **`/me`-style + resource routes**.

| Screen | Spec endpoint | Repo built |
| --- | --- | --- |
| Dashboard | `GET /api/v1/dashboard/student/{user_id}` | `/students/me/dashboard` |
| Academics | `GET /api/v1/academics/{user_id}` | (in academics/subjects) |
| Attendance | `GET /api/v1/attendance/{user_id}` ; faculty `POST /api/v1/attendance` ; `PUT /attendance/{id}` | `/attendance/summary`,`/overall`,`/records` |
| Marks | `GET /api/v1/marks/{user_id}` ; `POST /api/v1/marks` ; `PUT /marks/{id}` | `/results`,`/results/gpa` |
| Progress | `GET /api/v1/progress/{user_id}` | (in analytics) |
| Fees | `GET /api/v1/fees/{user_id}` ; `POST /fees` ; `POST /fees/assign` ; `PUT /fees/{id}` ; **`POST /fees/payment`** ; **`GET /fees/receipt/{payment_id}`** | `/fees`,`/fees/{id}/pay`,`/fees/total-due` |
| Transport | `GET /api/v1/transport/{user_id}` ; `POST /transport/routes` ; `POST /transport/allocate` ; `POST /transport/location` | `/transport/routes`,`/routes/{id}/live` |
| Notifications | `GET /api/v1/notifications/{user_id}` ; `GET /notifications/unread/{user_id}` ; **`PUT /notifications/read/{notification_id}`** ; `POST /notifications` | `/notifications`,`/unread-count`,`/{id}/read` |
| Leaves | `POST /api/v1/leaves` ; `PUT /leaves/{leave_id}` ; `GET /leaves/{user_id}` ; **`GET /leaves/parent/{user_id}`** | `/leaves`,`/{id}/approve`,`/{id}/reject` |
| Student profile | `GET /api/v1/students/{user_id}` | `/students/me` |
| Parent profile | `GET /api/v1/parents/{user_id}` ; `POST /parents` ; `PUT /parents/{id}` | guardians app |
| Chat | `POST /api/v1/chat` ; `POST /chat/message` ; `GET /chat/{user_id}` | `/chat/threads…` |
| Switch role | `GET /api/v1/auth/roles/{user_id}` ; `POST /api/v1/auth/switch-role` → `{access_token, active_role}` | `/auth/switch-role` (diff shape) |
| Logout | `POST /api/v1/auth/logout` (remove Redis session, mark inactive, revoke, timestamp) | present (no session table) |

**Common rules (spec):** every GET = validate JWT → active session → **college_id** → fetch by `user_id` → Redis-first (TTL 30m); every POST/PUT = validate JWT → permission → validate payload → save → **audit log** → invalidate cache.

## G. Modules to implement (spec lists 22)
auth, students, parents, faculty, attendance, academics, examinations, timetable, fees, hostel,
library, transport, placement, **AI Mentor, AI Chat, AI Notes, AI Resume Builder**, notifications,
dashboard & analytics, chat & messaging, reports, file management.
- Repo has 24 apps covering most; **AI is one `ai` app** (spec wants Mentor/Chat/Notes/Resume as first-class), **reports** + **file management** not first-class, **examinations vs my `exams`** naming, **timetable** folded into academics.

---

## H. Gap summary (what "wrong/missing" means, prioritized)
**Integration-breaking (contract):**
1. Envelope `success`→`status`.
2. Endpoint paths → doc's `{user_id}` shapes (dashboard/student, attendance, marks, fees(+payment/receipt), transport, notifications(read/unread), leaves(+parent), academics, progress, chat, switch-role, parents).
3. Field casing → snake_case (per doc).
4. Pagination param `page_size`→`limit`.

**Architecture (spec-mandated):**
5. **Multi-tenancy: `college_id` on every model + College model + tenant isolation** (biggest).
6. `BaseModel`: add `college_id`, `is_active`.
7. Auth: DB `roles`/`permissions`/`role_permissions`, `user_sessions`, `login_history`; single-active-login; account locking; password policy (complexity/history/expiry); username/phone login; email verification; OTP email+SMS.
8. AuditLog: add `module`, `previous_value`, `current_value`, `device`; log login/logout/role/password.
9. Role rename `admin`→`college_admin`.
10. Cache keys/TTL to spec (`dashboard:{user_id}`, 30m) + invalidation.

**Infra / quality:**
11. FCM push, Twilio SMS, SMTP; Nginx; structured logging; Swagger at `/api/schema/swagger-ui/` + `/redoc/`; ≥80% tests; README; file→S3 URL fields; AI Mentor/Chat/Notes/Resume as modules; reports + file-management modules.

## I. Proposed reconciliation (phased — awaiting your go-ahead on scope)
- **Phase 1 — Contract:** envelope→`status`, remap all endpoints to spec paths, snake_case responses (app maps snake→camel in `http.ts`), `limit` pagination, Swagger UI/redoc. → app talks to backend exactly per spec.
- **Phase 2 — Multi-tenancy + `BaseModel`:** College model, `college_id`+`is_active` on `BaseModel`, tenant-scoped managers/middleware, migrations, seed per-college.
- **Phase 3 — Auth to spec:** roles/permissions/role_permissions/user_sessions/login_history tables, single-active-login, account locking, password policy, username/phone login, OTP email/SMS, email verification, richer audit log.
- **Phase 4 — Module parity:** align examinations/timetable/parents naming + AI Mentor/Chat/Notes/Resume + reports + file management; snake_case + cache keys + audit everywhere.
- **Phase 5 — Infra/quality:** FCM/Twilio/SMTP, Nginx, structured logging, ≥80% tests, README.

**Open decisions for you:** (1) how far to go now (Phase 1 → 5?), (2) response casing (snake per doc + app maps ✅ recommended, or keep camel). Nothing will be built until you confirm scope.
