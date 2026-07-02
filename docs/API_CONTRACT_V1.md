# AI Campus OS — Mobile API Contract v1 (spec-exact)

The authoritative request/response contract for the mobile client, taken verbatim from the
Requirements doc + SRS + "Student/Parent Mobile App API Requirements". The backend must match this
exactly; the app consumes it (mapping to its internal types in the service `real` arms).

## Global
- **Envelope (success):** `{ "status": "success", "message": <str>, "data": <object|array> }`
- **Envelope (error):** `{ "status": "error", "message": <str>, "errors": [ ... ] }`
- **Casing:** snake_case (as in the spec examples).
- **Auth:** `Authorization: Bearer <access>`; every endpoint validates JWT + active session + college_id + role + user status.
- **Pagination (list endpoints):** `?page=&limit=&search=&ordering=&<filters>`; paginated `data` =
  `{ "results": [...], "pagination": { "count", "page", "limit", "total_pages", "next", "previous" } }`.
- **Status codes:** 200/201/400/401/403/404/409/422/500.
- `{user_id}` = the accounts user id. A student/parent may only access their own `user_id`; staff/admin any (within college).

## Auth
- `POST /api/v1/auth/login` — body `{ "username"|"email"|"phone", "password" }` → `data: { "access_token", "refresh_token", "user": {...}, "active_role" }`.
- `POST /api/v1/auth/refresh` — `{ "refresh_token" }` → `data: { "access_token" }`.
- `POST /api/v1/auth/logout` — revoke session/token → `{status:"success"}`.
- `GET  /api/v1/auth/me` → `data: user`.
- `GET  /api/v1/auth/roles/{user_id}` → `data: { "roles": ["STUDENT","PARENT",...] }`.
- `POST /api/v1/auth/switch-role` — `{ "role" }` → `data: { "access_token", "active_role" }`.
- `POST /api/v1/auth/change-password`, `/forgot-password`, `/reset-password`.

## Dashboard  (Redis `dashboard:{user_id}`, TTL 30m)
- `GET /api/v1/dashboard/student/{user_id}` →
  `data: { student_name, roll_no, department, semester, attendance_percentage, cgpa, pending_fees, pending_approvals, unread_chats, next_exam: { subject, time, room } }`

## Academics
- `GET /api/v1/academics/{user_id}` → `data: { degree, department, semester, section, mentor, cgpa }`
- `POST /api/v1/academics` · `PUT /api/v1/academics/{id}` (admin)

## Attendance
- `GET /api/v1/attendance/{user_id}` → `data: { overall_percentage, subject_wise: [ { subject, attended, total, percentage } ], monthly: [ { month, percentage } ] }`
- `POST /api/v1/attendance` (faculty create) · `PUT /api/v1/attendance/{attendance_id}` (update)

## Marks
- `GET /api/v1/marks/{user_id}` → `data: { subjects: [ { subject, internal, external, total, grade } ], gpa }`
- `POST /api/v1/marks` (faculty) · `PUT /api/v1/marks/{mark_id}`

## Academic Progress
- `GET /api/v1/progress/{user_id}` → `data: { gpa_trend: [ { semester, gpa } ], semester_gpa, overall_cgpa, ai_insights: [ ... ] }`
- `POST /api/v1/progress` (admin)

## Fees  (Redis `fees:{user_id}`)
- `GET /api/v1/fees/{user_id}` → `data: { total_due, paid_amount, pending_amount, invoices: [ { id, title, term, amount, due_date, status, paid_on } ] }`
- `POST /api/v1/fees` (admin create) · `POST /api/v1/fees/assign` · `PUT /api/v1/fees/{fee_id}`
- `POST /api/v1/fees/payment` — `{ fee_id }` → `data: { payment_id, receipt_no, ... }`
- `GET  /api/v1/fees/receipt/{payment_id}` → `data: receipt`

## Transport
- `GET /api/v1/transport/{user_id}` → `data: { route, driver, phone, live_location: {lat,lng}, eta, occupancy, stops: [...] }`
- `POST /api/v1/transport/routes` · `POST /api/v1/transport/allocate` · `POST /api/v1/transport/location`

## Notifications  (Redis `notifications:{user_id}`)
- `GET /api/v1/notifications/{user_id}` → `data: [ { id, title, body, category, is_read, created_at } ]`
- `GET /api/v1/notifications/unread/{user_id}` → `data: { unread_count }`
- `PUT /api/v1/notifications/read/{notification_id}` → mark read
- `POST /api/v1/notifications` (admin)

## Leaves
- `POST /api/v1/leaves` — student apply `{ type, from_date, to_date, reason }`
- `PUT  /api/v1/leaves/{leave_id}` — faculty approve/reject `{ status }`
- `GET  /api/v1/leaves/{user_id}` → student's leaves
- `GET  /api/v1/leaves/parent/{user_id}` → child's leaves for the parent

## Students / Parents
- `POST /api/v1/students` (admin) · `PUT /api/v1/students/{student_id}` · `DELETE` (soft)
- `GET  /api/v1/students/{user_id}` → `data: { name, email, phone, blood_group, mentor, admission_no, roll_no, department, semester, section }`
- `GET  /api/v1/students` (search: admission/roll/name/department/semester/section/year/status + pagination)
- `POST /api/v1/parents` · `PUT /api/v1/parents/{parent_id}` · `GET /api/v1/parents/{user_id}` → `data: { parent_name, mobile, email, children: [ { student_id, name, roll_no } ] }`

## Chat
- `POST /api/v1/chat` — create conversation
- `POST /api/v1/chat/message` — send `{ conversation_id, text }`
- `GET  /api/v1/chat/{user_id}` → conversations + history

## Common business rules
- **GET:** validate JWT → active session → college_id → fetch by user_id → Redis-first (TTL 30m) → standard JSON.
- **POST/PUT:** validate JWT → permission → validate payload → save → **audit log** → invalidate cache → success.

## App-side mapping (education-os)
`src/services/http.ts`: unwrap on `status === "success"` (throw on `"error"` with `message`+`errors`); for
paginated `data`, return `data.results`. Each service `real` arm calls the spec path (using the current
user_id) and maps the snake_case spec response → the app's camelCase type (types.ts). Screens/types unchanged.
