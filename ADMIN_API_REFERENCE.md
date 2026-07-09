# Admin Dashboard — API Reference

**Base URL:** `http://127.0.0.1:8000`  
**Common Headers (All requests):**
```
Authorization: Bearer <admin_access_token>
Content-Type: application/json
```

---

## 0. Get Admin Access Token

### Create Admin (First time only — CLI)
```powershell
$env:DJANGO_SUPERUSER_PASSWORD="Admin@123"
python manage.py createsuperuser --email admin@example.com --full_name "Admin User" --noinput
```

### Login
```
POST /api/v1/auth/login
```
```json
{
  "email": "admin@example.com",
  "password": "Admin@123"
}
```
**Response:**
```json
{
  "status": "success",
  "data": {
    "user": { "id": "uuid", "name": "Admin User", "role": "super_admin" },
    "access_token": "eyJ...",
    "refresh_token": "eyJ...",
    "active_role": "super_admin"
  }
}
```
→ Use `access_token` in all API calls below.

### Refresh (When access_token expires — 30 min)
```
POST /api/v1/auth/refresh
```
```json
{ "refresh": "<your-refresh-token>" }
```
→ Returns new `access_token` + `refresh_token`.

### Logout
```
POST /api/v1/auth/logout
```
```json
{ "refresh": "<your-refresh-token>" }
```

---

## 1. Add New Student

**API:** `POST /api/v1/auth/register`

**Request:**
```json
{
  "email": "student@college.edu",
  "full_name": "Ravi Kumar",
  "role": "student",
  "password": "Student@123",
  "phone": "9876543210",
  "roll_no": "22CSE042",
  "admission_no": "ADM2022042",
  "department": "<dept-uuid>",
  "program": "<program-uuid>",
  "semester": "<semester-uuid>",
  "section": "<section-uuid>",
  "gender": "male",
  "dob": "2003-07-15",
  "blood_group": "B+",
  "mentor_name": "Dr. Ramesh"
}
```

**With profile pic** → use `multipart/form-data` instead of JSON, add `profile_pic` file field.

**Response (201):**
```json
{
  "status": "success",
  "data": {
    "id": "user-uuid",
    "name": "Ravi Kumar",
    "email": "student@college.edu",
    "role": "student",
    "avatarColor": "#2563EB",
    "profilePic": null,
    "phone": "9876543210",
    "is_active": true,
    "student_id": "student-profile-uuid",
    "roll_no": "22CSE042"
  }
}
```

**Dropdown APIs:**

| Field | API |
|-------|-----|
| Department | `GET /api/v1/departments/` |
| Program | `GET /api/v1/programs/?department=<uuid>` |
| Semester | `GET /api/v1/semesters/?program=<uuid>` |
| Section | `GET /api/v1/sections/?semester=<uuid>` |

---

## 2. Add Department

**API:** `POST /api/v1/departments/`

**Request:**
```json
{
  "code": "CSE",
  "name": "Computer Science & Engineering",
  "hod": "<faculty-user-uuid>"
}
```

**Response (201):**
```json
{
  "status": "success",
  "data": {
    "id": "uuid",
    "code": "CSE",
    "name": "Computer Science & Engineering",
    "hod": "uuid",
    "hod_name": "Dr. Ramesh",
    "created_at": "...",
    "updated_at": "..."
  }
}
```

**Dropdown APIs:**

| Field | API |
|-------|-----|
| HOD (optional) | `GET /api/v1/departments/hod-candidates` |

---

## 3. Add Subject

**API:** `POST /api/v1/subjects/`

**Request:**
```json
{
  "code": "CS301",
  "name": "Data Structures & Algorithms",
  "credits": 4,
  "department": "<dept-uuid>",
  "semester": "<semester-uuid>",
  "faculty": "<faculty-user-uuid>",
  "color": "#2196F3"
}
```

**Response (201):**
```json
{
  "status": "success",
  "data": {
    "id": "uuid",
    "code": "CS301",
    "name": "Data Structures & Algorithms",
    "credits": 4,
    "department": "uuid",
    "department_code": "CSE",
    "semester": "uuid",
    "semester_number": 3,
    "program_code": "BTECH-CSE",
    "faculty": "uuid",
    "faculty_name": "Dr. Ramesh",
    "faculty_email": "ramesh@college.edu",
    "color": "#2196F3"
  }
}
```

**Dropdown APIs:**

| Field | API |
|-------|-----|
| Department | `GET /api/v1/departments/` |
| Program | `GET /api/v1/programs/?department=<uuid>` |
| Semester | `GET /api/v1/semesters/?program=<uuid>` |
| Faculty | `GET /api/v1/subjects/faculty-candidates` |

---

## 4. Timetable (Add Session)

**API:** `POST /api/v1/timetable/`

**Request:**
```json
{
  "subject": "<subject-uuid>",
  "section": "<section-uuid>",
  "faculty": "<faculty-user-uuid>",
  "day": "Mon",
  "start": "09:00",
  "end": "10:00",
  "room": "LH-1",
  "type": "Lecture"
}
```

**Response (201):**
```json
{
  "status": "success",
  "data": {
    "id": "uuid",
    "subject": "uuid",
    "section": "uuid",
    "faculty": "uuid",
    "faculty_name": "Dr. Ramesh",
    "day": "Mon",
    "start": "09:00",
    "end": "10:00",
    "room": "LH-1",
    "type": "Lecture"
  }
}
```

**Dropdown APIs:**

| Field | API | Notes |
|-------|-----|-------|
| Subject | `GET /api/v1/subjects/?semester=<uuid>` | Filtered by semester |
| Section | `GET /api/v1/sections/?semester=<uuid>` | Filtered by semester |
| Faculty | `GET /api/v1/subjects/faculty-candidates` | All active faculty |
| Day | Hardcoded | Mon, Tue, Wed, Thu, Fri, Sat |
| Type | Hardcoded | Lecture, Lab, Tutorial |

**View timetable:**

| Action | API |
|--------|-----|
| By section | `GET /api/v1/timetable/?section=<uuid>` |
| Today | `GET /api/v1/timetable/today` |
| Full week | `GET /api/v1/timetable/week` |

---

## 5. Attendance

### Mark Attendance (Faculty/Admin)

**API:** `POST /api/v1/attendance`

**Request:**
```json
{
  "classId": "<faculty-class-uuid>",
  "date": "2025-07-09",
  "period": 3,
  "entries": [
    { "studentId": "uuid-1", "status": "present" },
    { "studentId": "uuid-2", "status": "absent" },
    { "studentId": "uuid-3", "status": "late" }
  ]
}
```

**Status options:** `present`, `absent`, `late`

**Response (201):**
```json
{
  "status": "success",
  "data": {
    "id": "session-uuid",
    "classId": "uuid",
    "date": "2025-07-09",
    "entries": [
      { "studentId": "uuid-1", "status": "present" },
      { "studentId": "uuid-2", "status": "absent" }
    ]
  }
}
```

### View/Manage (Admin)

| Action | API |
|--------|-----|
| List all records | `GET /api/v1/attendance/manage/` |
| View student's attendance | `GET /api/v1/attendance/<user_id>` |
| Edit a record | `PATCH /api/v1/attendance/manage/<id>/` |
| Summary by student | `GET /api/v1/attendance/summary` |
| Overall % | `GET /api/v1/attendance/overall` |

### Dropdown APIs

| Field | API |
|-------|-----|
| Today's periods | `GET /api/v1/timetable/today` |
| Student roster | `GET /api/v1/faculty/classes/<id>/roster/` |

---

## 6. Fees

### Create Invoice (Admin)

**API:** `POST /api/v1/fees/`

**Request:**
```json
{
  "student": "<student-profile-uuid>",
  "title": "Tuition Fee - Sem 5",
  "term": "2025-odd",
  "amount": 50000.00,
  "due_date": "2025-08-15"
}
```

**Response (201):**
```json
{
  "status": "success",
  "data": {
    "id": "invoice-uuid",
    "student": "uuid",
    "title": "Tuition Fee - Sem 5",
    "term": "2025-odd",
    "amount": 50000.00,
    "dueDate": "2025-08-15",
    "status": "pending",
    "paidOn": null
  }
}
```

### Record Payment

**API:** `POST /api/v1/fees/payment`

**Request:**
```json
{
  "fee_id": "<invoice-uuid>",
  "amount": 50000.00,
  "method": "upi",
  "reference": "TXN123456789"
}
```

**Payment methods:** `upi`, `card`, `netbanking`, `cash`, `cheque`, `other`

**Response (201):**
```json
{
  "status": "success",
  "data": {
    "payment_id": "uuid",
    "receipt_no": "RCP-2025-0042"
  }
}
```

### Other Fee APIs

| Action | API | Method |
|--------|-----|--------|
| List all invoices | `/api/v1/fees/` | GET |
| Student's fee summary | `/api/v1/fees/<user-uuid>` | GET |
| Update invoice | `/api/v1/fees/<invoice-uuid>` | PUT/PATCH |
| Delete invoice | `/api/v1/fees/<invoice-uuid>` | DELETE |
| Get receipt | `/api/v1/fees/receipt/<payment-uuid>` | GET |
| Total due | `/api/v1/fees/total-due` | GET |

### Dropdown APIs

| Field | API |
|-------|-----|
| Student | `GET /api/v1/students/` |
| Payment method | Hardcoded: upi, card, netbanking, cash, cheque, other |

---

## 7. Supporting Setup APIs

These must be created first (in order) before students/subjects/timetable.

| # | Resource | API | Request |
|---|----------|-----|---------|
| 1 | Department | `POST /api/v1/departments/` | `{ "code": "CSE", "name": "..." }` |
| 2 | Program | `POST /api/v1/programs/` | `{ "code": "BTECH-CSE", "name": "...", "department": "<uuid>", "duration_years": 4, "intake": 120 }` |
| 3 | Semester | `POST /api/v1/semesters/` | `{ "program": "<uuid>", "number": 1 }` |
| 4 | Section | `POST /api/v1/sections/` | `{ "semester": "<uuid>", "name": "A" }` |
| 5 | Faculty | `POST /api/v1/auth/register` | `{ "email": "...", "full_name": "...", "role": "faculty", "password": "..." }` |

---

## 8. Error Responses

**401 — Token expired:**
```json
{ "status": "error", "data": { "detail": "Given token not valid for any token type" } }
```
→ Call `POST /api/v1/auth/refresh`

**403 — Wrong role:**
```json
{ "status": "error", "data": { "detail": "You do not have permission to perform this action." } }
```

**400 — Validation error:**
```json
{
  "status": "error",
  "data": {
    "email": ["A user with this email already exists."],
    "roll_no": ["A student with this roll number already exists."]
  }
}
```

**404 — Not found:**
```json
{ "status": "error", "data": { "detail": "Not found." } }
```


---

## 9. Library

### Add Book (Admin)

**API:** `POST /api/v1/library/books-admin/`

**Request:**
```json
{
  "title": "Introduction to Algorithms",
  "author": "Cormen, Leiserson, Rivest, Stein",
  "category": "Computer Science",
  "isbn": "978-0262033848",
  "copies_total": 10,
  "copies_available": 10
}
```

**Response (201):**
```json
{
  "status": "success",
  "data": {
    "id": "book-uuid",
    "title": "Introduction to Algorithms",
    "author": "Cormen, Leiserson, Rivest, Stein",
    "category": "Computer Science",
    "isbn": "978-0262033848",
    "available": true,
    "copies_total": 10,
    "copies_available": 10,
    "created_at": "...",
    "updated_at": "..."
  }
}
```

### Issue Book (Create Loan)

**API:** `POST /api/v1/library/loans-admin/`

**Request:**
```json
{
  "book": "<book-uuid>",
  "student": "<student-profile-uuid>",
  "issued_on": "2025-07-09",
  "due_on": "2025-07-23",
  "status": "active"
}
```

**Response (201):**
```json
{
  "status": "success",
  "data": {
    "id": "loan-uuid",
    "book": "book-uuid",
    "student": "student-uuid",
    "issued_on": "2025-07-09",
    "due_on": "2025-07-23",
    "returned_on": null,
    "status": "active"
  }
}
```

### Return Book (Update Loan)

**API:** `PATCH /api/v1/library/loans-admin/<loan-uuid>/`

**Request:**
```json
{
  "returned_on": "2025-07-20",
  "status": "returned"
}
```

### Other Library APIs

| Action | API | Method |
|--------|-----|--------|
| List all books | `/api/v1/library/books-admin/` | GET |
| Update book | `/api/v1/library/books-admin/<uuid>/` | PUT/PATCH |
| Delete book | `/api/v1/library/books-admin/<uuid>/` | DELETE |
| List all loans | `/api/v1/library/loans-admin/` | GET |
| Search books (student view) | `/api/v1/library/books?q=algorithms` | GET |
| Student's own loans | `/api/v1/library/loans` | GET |

### Dropdown APIs

| Field | API |
|-------|-----|
| Book | `GET /api/v1/library/books-admin/` |
| Student | `GET /api/v1/students/` |


---

## 10. Hostel

### Add Block (Admin)

**API:** `POST /api/v1/hostel-blocks/`

**Request:**
```json
{
  "name": "Block A",
  "warden": "Mr. Kumar",
  "warden_phone": "9876543210"
}
```

**Response (201):**
```json
{
  "status": "success",
  "data": {
    "id": "block-uuid",
    "name": "Block A",
    "warden": "Mr. Kumar",
    "warden_phone": "9876543210",
    "created_at": "...",
    "updated_at": "..."
  }
}
```

### Add Room

**API:** `POST /api/v1/hostel-rooms/`

**Request:**
```json
{
  "block": "<block-uuid>",
  "room_no": "A-201",
  "capacity": 3
}
```

**Response (201):**
```json
{
  "status": "success",
  "data": {
    "id": "room-uuid",
    "block": "block-uuid",
    "block_name": "Block A",
    "room_no": "A-201",
    "capacity": 3
  }
}
```

### Allocate Student to Room

**API:** `POST /api/v1/hostel/`

**Request:**
```json
{
  "student": "<student-profile-uuid>",
  "room": "<room-uuid>",
  "bed": "Lower",
  "mess_plan": "Veg",
  "fees": 25000.00
}
```

**Response (201):**
```json
{
  "status": "success",
  "data": {
    "id": "allocation-uuid",
    "student": "student-uuid",
    "room": "room-uuid",
    "room_no": "A-201",
    "block": "Block A",
    "warden": "Mr. Kumar",
    "bed": "Lower",
    "mess_plan": "Veg",
    "fees": 25000.00
  }
}
```

### Other Hostel APIs

| Action | API | Method |
|--------|-----|--------|
| List blocks | `/api/v1/hostel-blocks/` | GET |
| Update block | `/api/v1/hostel-blocks/<uuid>/` | PUT/PATCH |
| Delete block | `/api/v1/hostel-blocks/<uuid>/` | DELETE |
| List rooms | `/api/v1/hostel-rooms/` | GET |
| Update room | `/api/v1/hostel-rooms/<uuid>/` | PUT/PATCH |
| List allocations | `/api/v1/hostel/` | GET |
| Update allocation | `/api/v1/hostel/<uuid>/` | PUT/PATCH |
| Delete allocation | `/api/v1/hostel/<uuid>/` | DELETE |
| Student's hostel info | `/api/v1/hostel/info` | GET |

### Dropdown APIs

| Field | API |
|-------|-----|
| Block | `GET /api/v1/hostel-blocks/` |
| Room | `GET /api/v1/hostel-rooms/?block=<uuid>` |
| Student | `GET /api/v1/students/` |

### Setup Order

```
1. Create blocks (Block A, Block B, ...)
2. Create rooms (needs block)
3. Allocate students to rooms (needs student + room)
```


---

## 11. Transport

### Add Bus Route

**API:** `POST /api/v1/transport/routes/`

**Request:**
```json
{
  "name": "Route 5 - City Center",
  "number": "R5",
  "driver": "Raju K",
  "driver_phone": "9876543210"
}
```

**Response (201):**
```json
{
  "status": "success",
  "data": {
    "id": "route-uuid",
    "name": "Route 5 - City Center",
    "number": "R5",
    "driver": "Raju K",
    "driver_phone": "9876543210",
    "created_at": "...",
    "updated_at": "..."
  }
}
```

### Add Bus Stop

**API:** `POST /api/v1/transport/stops/`

**Request:**
```json
{
  "route": "<route-uuid>",
  "name": "Main Gate",
  "time": "07:30",
  "order": 1
}
```

**Response (201):**
```json
{
  "status": "success",
  "data": {
    "id": "stop-uuid",
    "route": "route-uuid",
    "name": "Main Gate",
    "time": "07:30",
    "order": 1
  }
}
```

### Update Live Status

**API:** `POST /api/v1/transport/live-status/`

**Request:**
```json
{
  "route": "<route-uuid>",
  "current_stop": "City Center",
  "next_stop": "Main Gate",
  "eta_mins": 12,
  "occupancy": 35,
  "lat": 12.9716,
  "lng": 77.5946
}
```

### View Student's Transport

**API:** `GET /api/v1/transport/<user-uuid>`

**Response:**
```json
{
  "status": "success",
  "data": {
    "route": "Route 5 - City Center",
    "driver": "Raju K",
    "phone": "9876543210",
    "live_location": { "lat": 12.9716, "lng": 77.5946 },
    "eta": 12,
    "occupancy": 35,
    "stops": [
      { "name": "Main Gate", "time": "07:30" },
      { "name": "City Center", "time": "08:00" }
    ]
  }
}
```

### Other Transport APIs

| Action | API | Method |
|--------|-----|--------|
| List routes | `/api/v1/transport/routes/` | GET |
| Update route | `/api/v1/transport/routes/<uuid>/` | PUT/PATCH |
| Delete route | `/api/v1/transport/routes/<uuid>/` | DELETE |
| List stops | `/api/v1/transport/stops/` | GET |
| Update stop | `/api/v1/transport/stops/<uuid>/` | PUT/PATCH |
| Delete stop | `/api/v1/transport/stops/<uuid>/` | DELETE |
| List live statuses | `/api/v1/transport/live-status/` | GET |
| Update live status | `/api/v1/transport/live-status/<uuid>/` | PUT/PATCH |

### Dropdown APIs

| Field | API |
|-------|-----|
| Route | `GET /api/v1/transport/routes/` |

### Setup Order

```
1. Create routes (Route 1, Route 2, ...)
2. Add stops to each route (needs route)
3. Update live status (GPS tracking — optional)
```


---

## 12. Exams & Results

### Add Exam

**API:** `POST /api/v1/exams/`

**Request:**
```json
{
  "subject": "<subject-uuid>",
  "name": "Mid Semester Exam",
  "date": "2025-04-15",
  "time": "10:00",
  "room": "Hall-A",
  "duration_mins": 120,
  "type": "mid"
}
```

**Response (201):**
```json
{
  "status": "success",
  "data": {
    "id": "exam-uuid",
    "subject": "uuid",
    "subject_code": "CS301",
    "subject_name": "Data Structures",
    "name": "Mid Semester Exam",
    "date": "2025-04-15",
    "time": "10:00",
    "room": "Hall-A",
    "duration_mins": 120,
    "type": "mid"
  }
}
```

### Add Result (Per Student)

**API:** `POST /api/v1/results/`

**Request:**
```json
{
  "student": "<student-profile-uuid>",
  "subject": "<subject-uuid>",
  "exam_ref": "<exam-uuid>",
  "exam": "Mid Semester",
  "marks": 85.00,
  "max_marks": 100.00,
  "grade": "A",
  "grade_point": 9.00,
  "credits": 4
}
```

**Response (201):**
```json
{
  "status": "success",
  "data": {
    "id": "result-uuid",
    "student": "uuid",
    "subject": "uuid",
    "exam_ref": "uuid",
    "exam": "Mid Semester",
    "marks": 85.00,
    "max_marks": 100.00,
    "grade": "A",
    "grade_point": 9.00,
    "credits": 4
  }
}
```

### Bulk Marks Entry (Faculty)

**API:** `POST /api/v1/marks/`

**Request:**
```json
{
  "classId": "<faculty-class-uuid>",
  "exam": "Mid Semester",
  "maxMarks": 100.00,
  "entries": [
    { "studentId": "uuid-1", "marks": 85.00 },
    { "studentId": "uuid-2", "marks": 72.50 },
    { "studentId": "uuid-3", "marks": 91.00 }
  ]
}
```

**Response (201):**
```json
{
  "status": "success",
  "data": {
    "id": "sheet-uuid",
    "classId": "uuid",
    "exam": "Mid Semester",
    "maxMarks": 100.00,
    "enteredOn": "2025-04-20T12:00:00Z",
    "entries": [
      { "studentId": "uuid-1", "marks": 85.00 },
      { "studentId": "uuid-2", "marks": 72.50 },
      { "studentId": "uuid-3", "marks": 91.00 }
    ]
  }
}
```

### View APIs

| Action | API | Method |
|--------|-----|--------|
| List exams | `/api/v1/exams/` | GET |
| Upcoming exams | `/api/v1/exams/upcoming/` | GET |
| List results | `/api/v1/results/` | GET |
| GPA summary | `/api/v1/results/gpa/` | GET |
| Student's marks | `/api/v1/marks/<user-uuid>` | GET |
| Faculty's mark sheets | `/api/v1/faculty/marks/` | GET |
| Update exam | `/api/v1/exams/<uuid>/` | PUT/PATCH |
| Delete exam | `/api/v1/exams/<uuid>/` | DELETE |
| Update result | `/api/v1/results/<uuid>/` | PUT/PATCH |

### Dropdown APIs

| Field | API |
|-------|-----|
| Subject | `GET /api/v1/subjects/?semester=<uuid>` |
| Student | `GET /api/v1/students/` |
| Faculty class (for bulk marks) | `GET /api/v1/faculty/classes/` |
| Student roster (for bulk marks) | `GET /api/v1/faculty/classes/<id>/roster/` |


---

## 13. Notifications

### Send Notification to a User (Admin)

**API:** `POST /api/v1/notifications/`

**Request:**
```json
{
  "recipient": "<user-uuid>",
  "title": "Fee Payment Reminder",
  "body": "Your hostel fee is due by July 15.",
  "category": "fee"
}
```

**Categories:** `academic`, `fee`, `event`, `general`, `attendance`

**Response (201):**
```json
{
  "status": "success",
  "data": {
    "id": "notif-uuid",
    "recipient": "user-uuid",
    "broadcast_role": "",
    "title": "Fee Payment Reminder",
    "body": "Your hostel fee is due by July 15.",
    "category": "fee",
    "read": false,
    "created_at": "2025-07-09T10:00:00Z"
  }
}
```

### Broadcast to All Users of a Role

**API:** `POST /api/v1/notifications/broadcast`

**Request:**
```json
{
  "title": "Campus Closed Tomorrow",
  "body": "Due to heavy rains, campus will remain closed on July 10.",
  "category": "general",
  "role": "student"
}
```

Leave `role` empty to broadcast to everyone.

**Response (201):**
```json
{ "status": "success", "data": { "message": "Broadcast sent." } }
```

### View User's Notifications

**API:** `GET /api/v1/notifications/<user-uuid>`

**Response:**
```json
{
  "status": "success",
  "data": [
    {
      "id": "uuid-1",
      "title": "Fee Payment Reminder",
      "body": "Your hostel fee is due by July 15.",
      "category": "fee",
      "is_read": false,
      "created_at": "2025-07-09T10:00:00Z"
    },
    {
      "id": "uuid-2",
      "title": "Campus Closed Tomorrow",
      "body": "Due to heavy rains...",
      "category": "general",
      "is_read": true,
      "created_at": "2025-07-08T15:00:00Z"
    }
  ]
}
```

### Unread Count

**API:** `GET /api/v1/notifications/unread/<user-uuid>`

**Response:**
```json
{ "status": "success", "data": { "unread_count": 3 } }
```

### Mark as Read

**API:** `PUT /api/v1/notifications/read/<notification-uuid>`

**Response:**
```json
{ "status": "success", "data": { "message": "Marked as read." } }
```

### Mark All as Read

**API:** `POST /api/v1/notifications/read-all`

### Other APIs

| Action | API | Method |
|--------|-----|--------|
| List all (admin) | `/api/v1/notifications/` | GET |
| Delete notification | `/api/v1/notifications/<uuid>/` | DELETE |
| Unread count (self) | `/api/v1/notifications/unread-count` | GET |

### Dropdown APIs

| Field | API |
|-------|-----|
| Recipient (user) | `GET /api/v1/admin/users` |
| Role (for broadcast) | Hardcoded: student, faculty, parent, hod, admin |
| Category | Hardcoded: academic, fee, event, general, attendance |


---

## 14. Assignments

### Create Assignment (Faculty/Admin)

**API:** `POST /api/v1/assignments/`

**Request:**
```json
{
  "subject": "<subject-uuid>",
  "faculty_class": "<faculty-class-uuid>",
  "title": "DSA Problem Set 3",
  "description": "Solve problems 1-10 from chapter 5",
  "due_date": "2025-04-01T23:59:00Z",
  "max_marks": 100
}
```

**Response (201):**
```json
{
  "status": "success",
  "data": {
    "id": "uuid",
    "subject": "uuid",
    "subject_code": "CS301",
    "subject_name": "Data Structures",
    "title": "DSA Problem Set 3",
    "description": "Solve problems 1-10 from chapter 5",
    "due_date": "2025-04-01T23:59:00Z",
    "max_marks": 100,
    "status": "pending"
  }
}
```

### Student Views

| Action | API |
|--------|-----|
| List assignments | `GET /api/v1/assignments/?status=pending` |
| View one | `GET /api/v1/assignments/<uuid>/` |
| Submit | `POST /api/v1/assignments/<uuid>/submit/` |

**Submit Request:**
```json
{ "fileName": "assignment3_solution.pdf" }
```

### Faculty Views

| Action | API |
|--------|-----|
| My assignments | `GET /api/v1/faculty/assignments/` |

### Dropdown APIs

| Field | API |
|-------|-----|
| Subject | `GET /api/v1/subjects/?semester=<uuid>` |
| Faculty class | `GET /api/v1/faculty/classes/` |

---

## 15. Materials (Study Notes/PDFs)

### Upload Material (Faculty/Admin)

**API:** `POST /api/v1/materials/`

**Request:**
```json
{
  "subject": "<subject-uuid>",
  "faculty_class": "<faculty-class-uuid>",
  "title": "Week 5 - Trees & Graphs",
  "kind": "note",
  "size_label": "2.4 MB",
  "url": "https://storage.example.com/notes/week5.pdf"
}
```

**Kind options:** `note`, `pdf`, `link`, `video`

### Student View

**API:** `GET /api/v1/materials/?subjectId=<uuid>`

**Response item:**
```json
{
  "id": "uuid",
  "subjectId": "uuid",
  "title": "Week 5 - Trees & Graphs",
  "kind": "note",
  "sizeLabel": "2.4 MB",
  "addedAt": "2025-03-10T10:00:00Z"
}
```

### Faculty View

**API:** `GET /api/v1/materials/faculty/?classId=<uuid>`

---

## 16. Quizzes

### Create Quiz (Faculty)

**API:** `POST /api/v1/quizzes/`

**Request:**
```json
{
  "subjectId": "<subject-uuid>",
  "title": "DSA Quiz 3 - Trees",
  "questions": [
    {
      "q": "Which traversal visits root first?",
      "options": ["Inorder", "Preorder", "Postorder", "Level-order"],
      "answerIndex": 1
    },
    {
      "q": "Height of balanced BST with n nodes?",
      "options": ["O(n)", "O(log n)", "O(n²)", "O(1)"],
      "answerIndex": 1
    }
  ]
}
```

**Response (201):**
```json
{
  "status": "success",
  "data": {
    "id": "quiz-uuid",
    "subjectId": "uuid",
    "title": "DSA Quiz 3 - Trees",
    "questions": [
      { "id": "q-uuid-1", "q": "Which traversal visits root first?", "options": [...], "answerIndex": 1 },
      { "id": "q-uuid-2", "q": "Height of balanced BST...", "options": [...], "answerIndex": 1 }
    ]
  }
}
```

### Student View

**API:** `GET /api/v1/quizzes/`

---

## 17. Placements

### Create Opening (Admin)

**API:** `POST /api/v1/placements-admin/`

**Request:**
```json
{
  "company": "Google",
  "role": "Software Engineer",
  "ctc": 25.0,
  "location": "Bangalore",
  "eligibility": "CGPA >= 7.0, CSE/IT only",
  "last_date": "2025-05-15",
  "logo_color": "#4285F4",
  "is_active": true
}
```

### Student Views

| Action | API |
|--------|-----|
| List openings | `GET /api/v1/placements` |
| Apply | `POST /api/v1/placements/<uuid>/apply` |
| My applications | `GET /api/v1/placements/applications` |

### Admin Views

| Action | API |
|--------|-----|
| Stats | `GET /api/v1/placements/stats` |
| Manage applications | `GET /api/v1/placement-applications/` |
| Update application status | `PATCH /api/v1/placement-applications/<uuid>/` |

---

## 18. Events

### Create Event (Admin)

**API:** `POST /api/v1/events-admin/`

**Request:**
```json
{
  "title": "Tech Fest 2025",
  "date": "2025-04-20",
  "time": "10:00",
  "venue": "Main Auditorium",
  "category": "cultural",
  "description": "Annual tech and cultural fest"
}
```

### Student Views

| Action | API |
|--------|-----|
| List events | `GET /api/v1/events` |
| Register/Unregister | `POST /api/v1/events/<uuid>/register` |

---

## 19. Complaints

### Student: File Complaint

**API:** `POST /api/v1/complaints`

**Request:**
```json
{
  "category": "Hostel",
  "subject": "Water leakage in room",
  "description": "Continuous water leakage from ceiling in room A-201."
}
```

### Student: View Own Complaints

**API:** `GET /api/v1/complaints`

### Admin: Update Status

**API:** `PATCH /api/v1/complaints/<uuid>/`

**Request:**
```json
{ "status": "in_progress" }
```

**Status options:** `open`, `in_progress`, `resolved`

### Admin: Monitor All

**API:** `GET /api/v1/complaints/monitor`

---

## 20. Leave

### Student: Apply Leave

**API:** `POST /api/v1/leaves`

**Request:**
```json
{
  "type": "sick",
  "from_date": "2025-04-05",
  "to_date": "2025-04-07",
  "reason": "Fever and cold"
}
```

### Student: View Leaves

**API:** `GET /api/v1/leaves`

### Admin/Faculty: Approve/Reject

**API:** `PUT /api/v1/leaves/<leave-uuid>`

**Request:**
```json
{ "status": "approved" }
```

**Status options:** `approved`, `rejected`

### Parent: View Child's Leaves

**API:** `GET /api/v1/leaves/parent/<user-uuid>`

---

## 21. Certificates

### Issue Certificate (Admin)

**API:** `POST /api/v1/certificates-admin/`

**Request:**
```json
{
  "student": "<student-profile-uuid>",
  "title": "Course Completion - Python",
  "issuer": "NPTEL",
  "issued_on": "2025-02-15",
  "kind": "course",
  "url": "https://nptel.ac.in/cert/..."
}
```

### Student: View Own Certificates

**API:** `GET /api/v1/certificates`

---

## 22. Chat (Parent ↔ Teacher)

### Create Conversation

**API:** `POST /api/v1/chat`

**Request:**
```json
{
  "teacher_id": "<faculty-user-uuid>",
  "subject_label": "Data Structures"
}
```

### Send Message

**API:** `POST /api/v1/chat/message`

**Request:**
```json
{
  "conversation_id": "<thread-uuid>",
  "text": "Hello, I wanted to discuss my child's performance."
}
```

### View Conversations

**API:** `GET /api/v1/chat/<user-uuid>`

---

## 23. AI Assistant

**Features:** `mentor`, `doubt`, `notes`, `assignment`, `resume`, `career`, `chat`

### Quick Response (No history)

**API:** `POST /api/v1/ai/{feature}/respond`

**Request:**
```json
{ "prompt": "Explain recursion in 3 lines" }
```

**Response:**
```json
{ "status": "success", "data": { "text": "Recursion is..." } }
```

### Chat with History

| Action | API |
|--------|-----|
| List threads | `GET /api/v1/ai/threads` |
| Get/create thread | `GET /api/v1/ai/threads/{feature}` |
| Send message | `POST /api/v1/ai/threads/{feature}/messages` |

**Send message request:**
```json
{ "text": "What career paths for CSE?" }
```

---

## 24. Student Dashboard

**API:** `GET /api/v1/students/me/dashboard/`

**Response:**
```json
{
  "status": "success",
  "data": {
    "student": { "id": "...", "name": "Ravi Kumar", "rollNo": "22CSE042" },
    "attendancePct": 89,
    "cgpa": 8.5,
    "pendingAssignments": 3,
    "todayClasses": [
      { "id": "...", "subjectId": "...", "day": "Mon", "start": "09:00", "end": "10:00", "room": "LH-1", "type": "Lecture" }
    ],
    "dueFees": 25000.00,
    "unread": 5,
    "nextExam": { "id": "...", "name": "Mid Sem", "date": "2025-04-15", "time": "10:00", "room": "Hall-A" }
  }
}
```

---

## 25. Parent Dashboard

**API:** `GET /api/v1/parent/dashboard/`

**Response:**
```json
{
  "status": "success",
  "data": {
    "child": { "id": "...", "name": "Ravi Kumar", "rollNo": "22CSE042" },
    "attendancePct": 89,
    "cgpa": 8.5,
    "dueFees": 25000.00,
    "pendingApprovals": 1,
    "unreadChats": 2,
    "unreadNotifications": 4,
    "nextExam": null
  }
}
```

---

## 26. Faculty Dashboard

**API:** `GET /api/v1/faculty/dashboard/`

**Response:**
```json
{
  "status": "success",
  "data": {
    "faculty": { "id": "...", "name": "Dr. Ramesh", "email": "ramesh@college.edu", "role": "faculty", "avatarColor": "#673AB7" },
    "classCount": 4,
    "studentCount": 240,
    "todayClasses": [
      { "class": { "subjectCode": "CS301", "section": "A" }, "slot": { "start": "09:00", "end": "10:00", "room": "LH-1" } }
    ],
    "pendingAssignments": 12,
    "quizCount": 5,
    "unreadNotifications": 3
  }
}
```
