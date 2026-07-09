# AI Campus OS — Complete API Documentation

**Base URL:** `http://127.0.0.1:8000/api/v1/`  
**Auth:** JWT Bearer token (`Authorization: Bearer <access_token>`)  
**Response Envelope:** All responses wrapped as `{ "status": "success"|"error", "data": {...} }`  
**Roles:** `super_admin`, `admin`, `principal`, `hod`, `faculty`, `parent`, `student`

---

## Table of Contents

1. [Authentication](#1-authentication)
2. [Students](#2-students)
3. [Faculty](#3-faculty)
4. [Guardians / Parents](#4-guardians--parents)
5. [Academics](#5-academics)
6. [Attendance](#6-attendance)
7. [Assignments](#7-assignments)
8. [Exams & Results](#8-exams--results)
9. [Fees](#9-fees)
10. [Library](#10-library)
11. [Hostel](#11-hostel)
12. [Transport](#12-transport)
13. [Materials](#13-materials)
14. [Quizzes](#14-quizzes)
15. [Placement](#15-placement)
16. [Notifications](#16-notifications)
17. [Events](#17-events)
18. [Complaints](#18-complaints)
19. [Leave](#19-leave)
20. [Certificates](#20-certificates)
21. [Chat](#21-chat)
22. [AI Assistant](#22-ai-assistant)
23. [Dashboards](#23-dashboards)
24. [Analytics (HOD & Principal)](#24-analytics-hod--principal)
25. [Administration](#25-administration)

---

## 1. Authentication

All auth endpoints are under `/api/v1/auth/`.

### POST `/auth/login`

Login with email/username/phone + password.

**Request:**
```json
{
  "email": "student@example.com",
  "password": "Student@123"
}
```

**Response (200):**
```json
{
  "status": "success",
  "data": {
    "user": {
      "id": "a1b2c3d4-...",
      "name": "John Doe",
      "email": "student@example.com",
      "role": "student",
      "avatarColor": "#4CAF50",
      "phone": "9876543210",
      "is_active": true
    },
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "active_role": "student"
  }
}
```

---

### POST `/auth/register`

Admin-only. Create a new user account.

**Headers:** `Authorization: Bearer <admin_token>`

**Request:**
```json
{
  "email": "newuser@example.com",
  "full_name": "New User",
  "role": "student",
  "password": "SecurePass@123",
  "phone": "9876543210",
  "avatar_color": "#FF5722"
}
```

**Response (201):**
```json
{
  "status": "success",
  "data": {
    "user": {
      "id": "uuid-...",
      "name": "New User",
      "email": "newuser@example.com",
      "role": "student",
      "avatarColor": "#FF5722",
      "phone": "9876543210",
      "is_active": true
    },
    "access_token": "eyJ...",
    "refresh_token": "eyJ..."
  }
}
```

---

### POST `/auth/refresh`

Refresh an expired access token.

**Request:**
```json
{
  "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Response (200):**
```json
{
  "status": "success",
  "data": {
    "user": { "id": "...", "name": "...", "email": "...", "role": "..." },
    "access_token": "eyJ...(new)...",
    "refresh_token": "eyJ...(new)...",
    "active_role": "student"
  }
}
```

---

### POST `/auth/logout`

Blacklist a refresh token.

**Request:**
```json
{
  "refresh": "eyJ..."
}
```

**Response (200):**
```json
{ "status": "success", "data": { "message": "Logged out." } }
```

---

### GET `/auth/me`

Get current authenticated user profile.

**Response (200):**
```json
{
  "status": "success",
  "data": {
    "id": "uuid-...",
    "name": "John Doe",
    "email": "student@example.com",
    "role": "student",
    "avatarColor": "#4CAF50",
    "phone": "9876543210",
    "is_active": true,
    "is_staff": false
  }
}
```

---

### GET `/auth/roles/{user_id}`

Get available roles for a user. Staff can query any user; students see only their own.

**Response (200):**
```json
{ "status": "success", "data": { "roles": ["student"] } }
```

---

### POST `/auth/switch-role`

Switch active role (for multi-role users).

**Request:**
```json
{ "role": "faculty" }
```

**Response (200):**
```json
{
  "status": "success",
  "data": {
    "access_token": "eyJ...(new token with role claim)...",
    "active_role": "faculty"
  }
}
```

---

### POST `/auth/change-password`

**Request:**
```json
{
  "current_password": "OldPass@123",
  "new_password": "NewPass@456"
}
```

**Response (200):**
```json
{ "status": "success", "data": { "message": "Password changed." } }
```

---

### POST `/auth/forgot-password`

Send OTP to email for password reset.

**Request:**
```json
{ "email": "user@example.com" }
```

**Response (200):**
```json
{ "status": "success", "data": { "message": "OTP sent." } }
```

---

### POST `/auth/reset-password`

Reset password using OTP.

**Request:**
```json
{
  "email": "user@example.com",
  "code": "123456",
  "new_password": "NewSecure@789"
}
```

**Response (200):**
```json
{ "status": "success", "data": { "message": "Password reset successfully." } }
```

---

## 2. Students

### GET `/students/me`

Get current student's own profile (mobile app shape).

**Response (200):**
```json
{
  "status": "success",
  "data": {
    "id": "uuid-...",
    "name": "John Doe",
    "rollNo": "20CSE101",
    "admissionNo": "ADM2020001",
    "program": "B.Tech Computer Science",
    "branch": "Computer Science & Engineering",
    "semester": 5,
    "section": "A",
    "year": 3,
    "cgpa": 8.5,
    "avatarColor": "#4CAF50",
    "email": "john@example.com",
    "phone": "9876543210",
    "mentorName": "Dr. Smith",
    "bloodGroup": "O+"
  }
}
```

---

### PUT `/students/me`

Update editable profile fields.

**Request:**
```json
{
  "name": "John Doe Updated",
  "phone": "9876543211",
  "avatarColor": "#2196F3",
  "bloodGroup": "A+"
}
```

**Response (200):** Same shape as `GET /students/me`.

---

### GET `/students/{user_id}`

Get student profile by user ID (spec-exact, staff or self).

**Response (200):**
```json
{
  "status": "success",
  "data": {
    "name": "John Doe",
    "email": "john@example.com",
    "phone": "9876543210",
    "blood_group": "O+",
    "mentor": "Dr. Smith",
    "admission_no": "ADM2020001",
    "roll_no": "20CSE101",
    "department": "Computer Science & Engineering",
    "semester": 5,
    "section": "A"
  }
}
```

---

### Admin CRUD: `/students/`

| Method | Path | Description |
|--------|------|-------------|
| GET | `/students/` | List all students (admin/staff, paginated) |
| POST | `/students/` | Create a student record |
| GET | `/students/{id}/` | Retrieve a student |
| PUT | `/students/{id}/` | Update a student |
| PATCH | `/students/{id}/` | Partial update |
| DELETE | `/students/{id}/` | Soft-delete |

**POST `/students/` Request:**
```json
{
  "user": "uuid-of-accounts-user",
  "roll_no": "20CSE101",
  "admission_no": "ADM2020001",
  "program": "uuid-of-program",
  "department": "uuid-of-department",
  "semester": "uuid-of-semester",
  "section": "uuid-of-section",
  "first_name": "John",
  "last_name": "Doe",
  "gender": "male",
  "dob": "2002-05-15",
  "phone": "9876543210",
  "email": "john@example.com",
  "blood_group": "O+",
  "mentor_name": "Dr. Smith"
}
```

---

### Sub-resources (Admin CRUD)

| Resource | Path |
|----------|------|
| Addresses | `/student-addresses/` |
| Guardians | `/student-guardians/` |
| Medical | `/student-medical/` |
| Documents | `/student-documents/` |

---

## 3. Faculty

### GET `/faculty/me`

Get authenticated faculty member's profile with their classes.

**Response (200):**
```json
{
  "status": "success",
  "data": {
    "faculty": {
      "id": "uuid-...",
      "name": "Dr. Smith",
      "email": "smith@example.com",
      "role": "faculty",
      "avatarColor": "#673AB7"
    },
    "department": "Computer Science & Engineering",
    "designation": "Assistant Professor",
    "classes": [
      {
        "id": "uuid-...",
        "subjectId": "uuid-...",
        "subjectCode": "CS301",
        "subjectName": "Data Structures",
        "semester": 3,
        "section": "A",
        "studentCount": 60,
        "color": "#2196F3",
        "slots": [
          { "day": "Monday", "start": "09:00", "end": "10:00", "room": "LH-1" }
        ]
      }
    ]
  }
}
```

---

### GET `/faculty/classes/`

List faculty's assigned classes.

### GET `/faculty/classes/{id}/roster/`

Get student roster for a class.

**Response (200):**
```json
{
  "status": "success",
  "data": [
    {
      "id": "uuid-student-ref",
      "name": "John Doe",
      "rollNo": "20CSE101",
      "avatarColor": "#4CAF50"
    }
  ]
}
```

---

### Admin CRUD: `/faculty/`

| Method | Path | Description |
|--------|------|-------------|
| GET | `/faculty/` | List all faculty profiles |
| POST | `/faculty/` | Create faculty profile |
| GET | `/faculty/{id}/` | Retrieve |
| PUT/PATCH | `/faculty/{id}/` | Update |
| DELETE | `/faculty/{id}/` | Soft-delete |

---

## 4. Guardians / Parents

### GET `/parents/{user_id}`

Get parent profile by user ID (spec route).

**Response (200):**
```json
{
  "status": "success",
  "data": {
    "parent_name": "Mr. Doe",
    "mobile": "9876543210",
    "email": "parent@example.com",
    "children": [
      {
        "student_id": "uuid-...",
        "name": "John Doe",
        "roll_no": "20CSE101"
      }
    ]
  }
}
```

---

### GET `/guardians/parent/children`

Get parent's children (mobile app shape — returns `StudentApp` objects with `relation`).

**Response (200):**
```json
{
  "status": "success",
  "data": [
    {
      "id": "uuid-...",
      "name": "John Doe",
      "rollNo": "20CSE101",
      "program": "B.Tech CSE",
      "branch": "CSE",
      "semester": 5,
      "section": "A",
      "year": 3,
      "cgpa": 8.5,
      "relation": "father"
    }
  ]
}
```

---

### Admin CRUD: `/guardians/`

Standard CRUD for parent-student link management.

---

## 5. Academics

### Admin CRUD Resources

| Resource | Path | Fields |
|----------|------|--------|
| Departments | `/departments/` | code, name |
| Programs | `/programs/` | code, name, department, duration_years, intake |
| Semesters | `/semesters/` | program, number |
| Sections | `/sections/` | semester, name |
| Subjects | `/subjects/` | code, name, credits, department, faculty_name, color |
| Timetable | `/timetable/` | subject, section, day, start, end, room, type |

---

### GET `/academics/{user_id}`

Get student's academic record.

**Response (200):**
```json
{
  "status": "success",
  "data": {
    "degree": "B.Tech",
    "department": "Computer Science & Engineering",
    "semester": 5,
    "section": "A",
    "mentor": "Dr. Smith",
    "cgpa": 8.5
  }
}
```

---

### GET `/progress/{user_id}`

Get student's academic progress (GPA trend + credits).

**Response (200):**
```json
{
  "status": "success",
  "data": {
    "gpaTrend": [
      { "semester": "Sem 1", "gpa": 8.2 },
      { "semester": "Sem 2", "gpa": 8.5 },
      { "semester": "Sem 3", "gpa": 8.8 }
    ],
    "creditsEarned": 90,
    "creditsRequired": 160
  }
}
```

---

### GET `/subjects/` (App-shaped)

Student's enrolled subjects.

**Response item:**
```json
{
  "id": "uuid-...",
  "code": "CS301",
  "name": "Data Structures",
  "credits": 4,
  "faculty": "Dr. Smith",
  "color": "#2196F3"
}
```

---

### GET `/timetable/week/`

Student's weekly timetable.

**Response item (ClassSession):**
```json
{
  "id": "uuid-...",
  "subjectId": "uuid-...",
  "day": "Monday",
  "start": "09:00",
  "end": "10:00",
  "room": "LH-1",
  "type": "lecture"
}
```

---

## 6. Attendance

### GET `/attendance/summary`

Student's per-subject attendance summary (self-scoped).

**Response (200):**
```json
{
  "status": "success",
  "data": [
    {
      "subjectId": "uuid-...",
      "subjectName": "Data Structures",
      "attended": 28,
      "total": 30,
      "percent": 93
    }
  ]
}
```

---

### GET `/attendance/overall`

Student's overall attendance percentage.

**Response (200):**
```json
{ "status": "success", "data": { "overall": 89 } }
```

---

### GET `/attendance/records?subjectId={uuid}`

Student's attendance records filtered by subject.

**Response item:**
```json
{
  "id": "uuid-...",
  "subjectId": "uuid-...",
  "date": "2025-03-15",
  "status": "present"
}
```

---

### GET `/attendance/{user_id}`

Student's attendance summary (spec route, staff or self).

---

### POST `/attendance`

Faculty: save an attendance session.

**Request:**
```json
{
  "classId": "uuid-faculty-class",
  "date": "2025-03-15",
  "entries": [
    { "studentId": "uuid-...", "status": "present" },
    { "studentId": "uuid-...", "status": "absent" },
    { "studentId": "uuid-...", "status": "late" }
  ]
}
```

**Response (201):**
```json
{
  "status": "success",
  "data": {
    "id": "uuid-session",
    "classId": "uuid-faculty-class",
    "date": "2025-03-15",
    "entries": [
      { "studentId": "uuid-...", "status": "present" },
      { "studentId": "uuid-...", "status": "absent" }
    ]
  }
}
```

---

### GET `/faculty/attendance?classId={uuid}`

Faculty's attendance sessions for a class.

---

### Admin CRUD: `/attendance/manage/`

Standard CRUD on raw AttendanceRecord rows.

---

## 7. Assignments

### GET `/assignments/?status={pending|submitted|graded|late}`

Student's assignments list (filtered by status).

**Response item (StudentAssignment):**
```json
{
  "id": "uuid-...",
  "subjectId": "uuid-...",
  "title": "DSA Problem Set 3",
  "description": "Solve problems 1-10 from chapter 5",
  "dueDate": "2025-04-01T23:59:00Z",
  "maxMarks": 100,
  "status": "pending",
  "submittedAt": null,
  "grade": null,
  "attachmentName": null
}
```

---

### GET `/assignments/{id}/`

Retrieve a single assignment detail.

---

### POST `/assignments/{id}/submit/`

Student submits an assignment.

**Request:**
```json
{ "fileName": "assignment3_solution.pdf" }
```

**Response (201):**
```json
{
  "status": "success",
  "data": {
    "id": "uuid-...",
    "subjectId": "uuid-...",
    "title": "DSA Problem Set 3",
    "status": "submitted",
    "submittedAt": "2025-03-28T14:30:00Z",
    "attachmentName": "assignment3_solution.pdf"
  }
}
```

---

### GET `/faculty/assignments/`

Faculty's created assignments list.

**Response item (FacultyAssignment):**
```json
{
  "id": "uuid-...",
  "subjectId": "uuid-...",
  "classId": "uuid-...",
  "title": "DSA Problem Set 3",
  "dueDate": "2025-04-01T23:59:00Z",
  "maxMarks": 100,
  "createdOn": "2025-03-20T10:00:00Z",
  "submissions": 45
}
```

---

### POST `/assignments/` (Faculty/Admin create)

**Request:**
```json
{
  "subject": "uuid-of-subject",
  "faculty_class": "uuid-of-faculty-class",
  "title": "DSA Problem Set 3",
  "description": "Solve problems 1-10",
  "due_date": "2025-04-01T23:59:00Z",
  "max_marks": 100
}
```

**Response (201):**
```json
{
  "status": "success",
  "data": {
    "id": "uuid-...",
    "subject": "uuid-...",
    "subject_code": "CS301",
    "subject_name": "Data Structures",
    "title": "DSA Problem Set 3",
    "due_date": "2025-04-01T23:59:00Z",
    "max_marks": 100,
    "status": "pending",
    "created_at": "2025-03-20T10:00:00Z"
  }
}
```

---

## 8. Exams & Results

### GET `/exams/`

List exams (student sees their semester's exams).

**Response item (Exam):**
```json
{
  "id": "uuid-...",
  "subjectId": "uuid-...",
  "name": "Mid Semester Exam",
  "date": "2025-04-15",
  "time": "10:00",
  "room": "Hall-A",
  "durationMins": 120,
  "type": "mid"
}
```

---

### GET `/exams/upcoming/`

Upcoming exams for the student.

---

### GET `/results/`

Student's exam results.

**Response item (ExamResult):**
```json
{
  "id": "uuid-...",
  "subjectId": "uuid-...",
  "subjectName": "Data Structures",
  "exam": "Mid Semester",
  "marks": 85.00,
  "maxMarks": 100.00,
  "grade": "A",
  "gradePoint": 9.00,
  "credits": 4
}
```

---

### GET `/results/gpa/`

GPA summary for the student.

---

### GET `/marks/{user_id}`

Student's marks breakdown (spec route).

---

### POST `/marks/`

Faculty: save a marks sheet.

**Request:**
```json
{
  "classId": "uuid-faculty-class",
  "exam": "Mid Semester",
  "maxMarks": 100.00,
  "entries": [
    { "studentId": "uuid-...", "marks": 85.00 },
    { "studentId": "uuid-...", "marks": 72.50 }
  ]
}
```

**Response (201):**
```json
{
  "status": "success",
  "data": {
    "id": "uuid-sheet",
    "classId": "uuid-faculty-class",
    "exam": "Mid Semester",
    "maxMarks": 100.00,
    "enteredOn": "2025-04-20T12:00:00Z",
    "entries": [
      { "studentId": "uuid-...", "marks": 85.00 },
      { "studentId": "uuid-...", "marks": 72.50 }
    ]
  }
}
```

---

### GET `/faculty/marks/`

Faculty's marks sheets.

---

## 9. Fees

### GET `/fees/{user_id}`

Fee summary and invoices for a user.

**Response (200):**
```json
{
  "status": "success",
  "data": {
    "total_due": 75000.00,
    "paid_amount": 50000.00,
    "pending_amount": 25000.00,
    "invoices": [
      {
        "id": "uuid-...",
        "title": "Tuition Fee - Sem 5",
        "term": "2025-odd",
        "amount": 50000.00,
        "due_date": "2025-06-30",
        "status": "paid",
        "paid_on": "2025-06-15T10:00:00Z"
      },
      {
        "id": "uuid-...",
        "title": "Hostel Fee - Sem 5",
        "term": "2025-odd",
        "amount": 25000.00,
        "due_date": "2025-07-15",
        "status": "pending",
        "paid_on": null
      }
    ]
  }
}
```

---

### POST `/fees/payment`

Record a payment.

**Request:**
```json
{
  "fee_id": "uuid-of-invoice",
  "amount": 25000.00,
  "method": "upi",
  "reference": "TXN123456789"
}
```

**Response (201):**
```json
{
  "status": "success",
  "data": {
    "payment_id": "uuid-...",
    "receipt_no": "RCP-2025-0042"
  }
}
```

---

### GET `/fees/receipt/{payment_id}`

Get payment receipt.

**Response (200):**
```json
{
  "status": "success",
  "data": {
    "payment_id": "uuid-...",
    "receipt_no": "RCP-2025-0042",
    "fee_id": "uuid-...",
    "title": "Hostel Fee - Sem 5",
    "term": "2025-odd",
    "amount": 25000.00,
    "method": "upi",
    "paid_at": "2025-07-10T14:30:00Z",
    "reference": "TXN123456789",
    "student_name": "John Doe",
    "roll_no": "20CSE101"
  }
}
```

---

### Admin CRUD: `/fees/`

| Method | Path | Description |
|--------|------|-------------|
| GET | `/fees/` | List all invoices |
| POST | `/fees/` | Create an invoice |
| PUT/PATCH | `/fees/{fee_id}` | Update an invoice |
| DELETE | `/fees/{fee_id}` | Soft-delete |
| GET | `/fees/total-due` | Total due for current user |
| POST | `/fees/{id}/pay` | Pay an invoice (legacy) |

---

## 10. Library

### GET `/library/books?q={search}`

Search the book catalogue.

**Response (200):**
```json
{
  "status": "success",
  "data": [
    {
      "id": "uuid-...",
      "title": "Introduction to Algorithms",
      "author": "Cormen, Leiserson, Rivest, Stein",
      "category": "Computer Science",
      "available": true
    }
  ]
}
```

---

### GET `/library/loans`

Current student's book loans.

**Response (200):**
```json
{
  "status": "success",
  "data": [
    {
      "id": "uuid-...",
      "bookId": "uuid-...",
      "title": "Introduction to Algorithms",
      "issuedOn": "2025-03-01",
      "dueOn": "2025-03-15",
      "status": "active"
    }
  ]
}
```

---

### Admin CRUD

| Resource | Path |
|----------|------|
| Books | `/library/books-admin/` |
| Loans | `/library/loans-admin/` |

---

## 11. Hostel

### GET `/hostel/info`

Current student's hostel allocation.

**Response (200):**
```json
{
  "status": "success",
  "data": {
    "block": "Block A",
    "roomNo": "A-201",
    "bed": "Lower",
    "warden": "Mr. Kumar",
    "wardenPhone": "9876543210",
    "messPlan": "Veg",
    "fees": 25000.0
  }
}
```

---

### Admin CRUD

| Resource | Path |
|----------|------|
| Allocations | `/hostel/` |
| Blocks | `/hostel-blocks/` |
| Rooms | `/hostel-rooms/` |

---

## 12. Transport

### GET `/transport/{user_id}`

Student's assigned bus route + live status.

**Response (200):**
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

---

### Admin CRUD

| Resource | Path |
|----------|------|
| Routes | `/transport/routes/` |
| Stops | `/transport/stops/` |
| Live Status | `/transport/live-status/` |

---

## 13. Materials

### GET `/materials/`

Student's study materials.

**Response item (Material):**
```json
{
  "id": "uuid-...",
  "subjectId": "uuid-...",
  "title": "DSA Lecture Notes - Week 5",
  "kind": "note",
  "sizeLabel": "2.4 MB",
  "addedAt": "2025-03-10T10:00:00Z"
}
```

---

### GET `/materials/faculty/`

Faculty's uploaded materials.

**Response item (FacultyMaterial):**
```json
{
  "id": "uuid-...",
  "classId": "uuid-...",
  "title": "DSA Lecture Notes - Week 5",
  "kind": "note",
  "sizeLabel": "2.4 MB",
  "addedOn": "2025-03-10T10:00:00Z"
}
```

---

### POST `/materials/`

Faculty: upload material metadata.

**Request:**
```json
{
  "subject": "uuid-of-subject",
  "faculty_class": "uuid-of-class",
  "title": "Week 5 Notes",
  "kind": "note",
  "size_label": "2.4 MB",
  "url": "https://storage.example.com/notes/week5.pdf"
}
```

**Response (201):** Full material record.

---

## 14. Quizzes

### GET `/quizzes/`

List quizzes available to the student.

**Response item (Quiz):**
```json
{
  "id": "uuid-...",
  "subjectId": "uuid-...",
  "title": "DSA Quiz 3 - Trees",
  "questions": [
    {
      "id": "uuid-...",
      "q": "Which traversal visits root first?",
      "options": ["Inorder", "Preorder", "Postorder", "Level-order"],
      "answerIndex": 1
    }
  ]
}
```

---

### POST `/quizzes/`

Faculty: create a quiz.

**Request:**
```json
{
  "subjectId": "uuid-of-subject",
  "title": "DSA Quiz 3 - Trees",
  "questions": [
    {
      "q": "Which traversal visits root first?",
      "options": ["Inorder", "Preorder", "Postorder", "Level-order"],
      "answerIndex": 1
    },
    {
      "q": "Height of a balanced BST with n nodes?",
      "options": ["O(n)", "O(log n)", "O(n²)", "O(1)"],
      "answerIndex": 1
    }
  ]
}
```

**Response (201):** Same as GET item (Quiz with nested questions).

---

## 15. Placement

### GET `/placements`

Active placement openings.

**Response item (PlacementOpening):**
```json
{
  "id": "uuid-...",
  "company": "Google",
  "role": "Software Engineer",
  "ctc": 25.0,
  "location": "Bangalore",
  "eligibility": "CGPA >= 7.0, CSE/IT only",
  "lastDate": "2025-05-15",
  "logoColor": "#4285F4",
  "applied": false
}
```

---

### POST `/placements/{id}/apply`

Student applies to an opening.

**Request:** No body required.

**Response (201):**
```json
{ "status": "success", "data": { "message": "Application submitted." } }
```

---

### GET `/placements/applications`

Student's own applications.

**Response item:**
```json
{
  "id": "uuid-...",
  "openingId": "uuid-...",
  "company": "Google",
  "role": "Software Engineer",
  "ctc": 25.0,
  "logoColor": "#4285F4",
  "status": "applied",
  "appliedOn": "2025-04-01"
}
```

---

### GET `/placements/stats`

Admin/principal placement statistics.

**Response (200):**
```json
{
  "status": "success",
  "data": {
    "placed": 120,
    "eligible": 300,
    "avgCtcLpa": 12.5,
    "highestCtcLpa": 45.0,
    "topRecruiters": ["Google", "Microsoft", "Amazon"],
    "openings": 25,
    "activeOpenings": 8,
    "totalApplications": 450,
    "byStatus": { "applied": 200, "shortlisted": 100, "selected": 120, "rejected": 30 }
  }
}
```

---

### Admin CRUD

| Resource | Path |
|----------|------|
| Openings | `/placements-admin/` |
| Applications | `/placement-applications/` |

---

## 16. Notifications

### GET `/notifications/{user_id}`

Get notifications for a user.

**Response (200):**
```json
{
  "status": "success",
  "data": [
    {
      "id": "uuid-...",
      "title": "Assignment Due Tomorrow",
      "body": "DSA Problem Set 3 is due by 11:59 PM.",
      "category": "academic",
      "is_read": false,
      "created_at": "2025-03-31T08:00:00Z"
    }
  ]
}
```

---

### GET `/notifications/unread/{user_id}`

Unread notification count.

**Response (200):**
```json
{ "status": "success", "data": { "unread_count": 5 } }
```

---

### PUT `/notifications/read/{notification_id}`

Mark a notification as read.

**Response (200):**
```json
{ "status": "success", "data": { "message": "Marked as read." } }
```

---

### Legacy Endpoints (Router)

| Method | Path | Description |
|--------|------|-------------|
| GET | `/notifications/` | Self-scoped notification list |
| POST | `/notifications/{id}/read` | Mark one as read |
| POST | `/notifications/read-all` | Mark all as read |
| GET | `/notifications/unread-count` | Unread count |
| POST | `/notifications/broadcast` | Admin: broadcast notification |

**POST `/notifications/broadcast` Request:**
```json
{
  "title": "Campus Closed Tomorrow",
  "body": "Due to heavy rains, campus will remain closed.",
  "category": "general",
  "role": "student"
}
```

---

## 17. Events

### GET `/events`

List campus events.

**Response item (EventItem):**
```json
{
  "id": "uuid-...",
  "title": "Tech Fest 2025",
  "date": "2025-04-20",
  "time": "10:00",
  "venue": "Main Auditorium",
  "category": "cultural",
  "registered": false
}
```

---

### POST `/events/{id}/register`

Toggle event registration for current user.

**Response (200):**
```json
{ "status": "success", "data": { "registered": true } }
```

---

### Admin CRUD: `/events-admin/`

Standard CRUD for events.

---

## 18. Complaints

### GET `/complaints`

List current user's complaints.

**Response (200):**
```json
{
  "status": "success",
  "data": [
    {
      "id": "uuid-...",
      "category": "Hostel",
      "subject": "Water leakage in room",
      "description": "There is continuous water leakage from ceiling in room A-201.",
      "status": "open",
      "createdOn": "2025-03-25T14:00:00Z"
    }
  ]
}
```

---

### POST `/complaints`

File a new complaint.

**Request:**
```json
{
  "category": "Hostel",
  "subject": "Water leakage in room",
  "description": "There is continuous water leakage from ceiling in room A-201."
}
```

**Response (201):**
```json
{
  "status": "success",
  "data": {
    "id": "uuid-...",
    "category": "Hostel",
    "subject": "Water leakage in room",
    "description": "There is continuous water leakage from ceiling in room A-201.",
    "status": "open",
    "createdOn": "2025-03-25T14:00:00Z"
  }
}
```

---

### PATCH `/complaints/{id}`

Staff: update complaint status.

**Request:**
```json
{ "status": "in_progress" }
```

**Response (200):** Updated complaint object.

---

### GET `/complaints/monitor`

Principal/Admin: all complaints + status counts.

**Response (200):**
```json
{
  "status": "success",
  "data": {
    "total": 42,
    "byStatus": [
      { "status": "open", "count": 15 },
      { "status": "in_progress", "count": 12 },
      { "status": "resolved", "count": 15 }
    ],
    "complaints": [ { "id": "...", "category": "...", "..." : "..." } ]
  }
}
```

---

## 19. Leave

### POST `/leaves`

Apply for leave.

**Request:**
```json
{
  "type": "sick",
  "from_date": "2025-04-05",
  "to_date": "2025-04-07",
  "reason": "Fever and cold"
}
```

**Response (201):**
```json
{
  "status": "success",
  "data": {
    "id": "uuid-...",
    "type": "sick",
    "from_date": "2025-04-05",
    "to_date": "2025-04-07",
    "reason": "Fever and cold",
    "status": "pending",
    "applied_on": "2025-04-04T10:00:00Z"
  }
}
```

---

### GET `/leaves`

List caller's leaves.

**Response item:**
```json
{
  "id": "uuid-...",
  "type": "sick",
  "from_date": "2025-04-05",
  "to_date": "2025-04-07",
  "reason": "Fever and cold",
  "status": "approved",
  "applied_on": "2025-04-04T10:00:00Z"
}
```

---

### GET `/leaves/{user_id}`

Get leaves for a specific user.

---

### PUT `/leaves/{leave_id}`

Approve or reject a leave request (staff).

**Request:**
```json
{ "status": "approved" }
```

**Response (200):** Updated leave object.

---

### GET `/leaves/parent/{user_id}`

Parent's children's leave requests.

---

### Legacy Actions

| Method | Path | Description |
|--------|------|-------------|
| POST | `/leaves/{id}/approve` | Approve a leave |
| POST | `/leaves/{id}/reject` | Reject a leave |

---

## 20. Certificates

### GET `/certificates`

Current student's certificates.

**Response (200):**
```json
{
  "status": "success",
  "data": [
    {
      "id": "uuid-...",
      "title": "Course Completion - Python",
      "issuer": "NPTEL",
      "issuedOn": "2025-02-15",
      "kind": "course",
      "url": "https://nptel.ac.in/cert/...",
      "fileUrl": "http://127.0.0.1:8000/media/certs/python_cert.pdf"
    }
  ]
}
```

---

### Admin CRUD: `/certificates-admin/`

| Method | Path | Description |
|--------|------|-------------|
| GET | `/certificates-admin/` | List all certificates |
| POST | `/certificates-admin/` | Issue a certificate |
| PATCH | `/certificates-admin/{id}/` | Update |
| DELETE | `/certificates-admin/{id}/` | Soft-delete |

**POST Request:**
```json
{
  "student": "uuid-of-student",
  "title": "Course Completion - Python",
  "issuer": "NPTEL",
  "issued_on": "2025-02-15",
  "kind": "course",
  "url": "https://nptel.ac.in/cert/..."
}
```

---

## 21. Chat

### POST `/chat`

Create a new conversation (parent↔teacher).

**Request:**
```json
{
  "teacher_id": "uuid-of-teacher",
  "subject_label": "Data Structures"
}
```

**Response (201):**
```json
{
  "status": "success",
  "data": {
    "id": "uuid-thread",
    "teacher_name": "Dr. Smith",
    "subject": "Data Structures",
    "avatar_color": "#673AB7",
    "last_message_at": null,
    "unread": 0,
    "messages": []
  }
}
```

---

### POST `/chat/message`

Send a message in a conversation.

**Request:**
```json
{
  "conversation_id": "uuid-thread",
  "text": "Hello, I wanted to discuss my child's performance."
}
```

**Response (201):**
```json
{
  "status": "success",
  "data": {
    "id": "uuid-msg",
    "sender": "parent",
    "text": "Hello, I wanted to discuss my child's performance.",
    "at": "2025-03-28T15:00:00Z"
  }
}
```

---

### GET `/chat/{user_id}`

Get a user's conversations with message history.

**Response (200):**
```json
{
  "status": "success",
  "data": [
    {
      "id": "uuid-thread",
      "teacher_name": "Dr. Smith",
      "subject": "Data Structures",
      "avatar_color": "#673AB7",
      "last_message_at": "2025-03-28T15:30:00Z",
      "unread": 2,
      "messages": [
        { "id": "uuid-...", "sender": "parent", "text": "Hello...", "at": "2025-03-28T15:00:00Z" },
        { "id": "uuid-...", "sender": "teacher", "text": "Hi, sure...", "at": "2025-03-28T15:30:00Z" }
      ]
    }
  ]
}
```

---

### Legacy Endpoints (Router)

| Method | Path | Description |
|--------|------|-------------|
| GET | `/chat/threads` | List threads (self-scoped) |
| GET | `/chat/threads/{id}` | Get one thread |
| POST | `/chat/threads/{id}/messages` | Send message |
| POST | `/chat/threads/{id}/read` | Mark thread read |

---

## 22. AI Assistant

Features: `mentor`, `doubt`, `notes`, `assignment`, `resume`, `career`, `chat`

### GET `/ai/threads`

List all AI threads for the current user.

**Response (200):**
```json
{
  "status": "success",
  "data": [
    {
      "id": "uuid-...",
      "feature": "mentor",
      "title": "AI Mentor",
      "messages": []
    },
    {
      "id": "uuid-...",
      "feature": "doubt",
      "title": "AI Doubt Solver",
      "messages": [
        { "id": "uuid-...", "role": "user", "text": "Explain BST", "at": "2025-03-28T10:00:00Z" },
        { "id": "uuid-...", "role": "assistant", "text": "A BST is...", "at": "2025-03-28T10:00:01Z" }
      ]
    }
  ]
}
```

---

### GET `/ai/threads/{feature}`

Get or create the thread for a specific feature.

**Example:** `GET /ai/threads/mentor`

**Response (200):**
```json
{
  "status": "success",
  "data": {
    "id": "uuid-...",
    "feature": "mentor",
    "title": "AI Mentor",
    "messages": []
  }
}
```

---

### POST `/ai/threads/{feature}/messages`

Send a message to the AI thread.

**Request:**
```json
{ "text": "What career paths are good for a CSE student?" }
```

**Response (201):**
```json
{
  "status": "success",
  "data": {
    "id": "uuid-thread",
    "feature": "career",
    "title": "AI Career Guide",
    "messages": [
      { "id": "uuid-...", "role": "user", "text": "What career paths...", "at": "..." },
      { "id": "uuid-...", "role": "assistant", "text": "Here are some paths...", "at": "..." }
    ]
  }
}
```

---

### POST `/ai/{feature}/respond`

Quick single-shot AI response (no thread persistence).

**Request:**
```json
{ "prompt": "Summarize the concept of recursion in 3 lines." }
```

**Response (200):**
```json
{
  "status": "success",
  "data": {
    "text": "Recursion is a technique where a function calls itself..."
  }
}
```

---

### GET `/ai/suggestions/{feature}`

Get AI-generated suggestions for a feature.

---

## 23. Dashboards

### GET `/dashboard/student/{user_id}`

Student dashboard (spec route).

**Response (200):**
```json
{
  "status": "success",
  "data": {
    "student_name": "John Doe",
    "roll_no": "20CSE101",
    "department": "Computer Science & Engineering",
    "semester": 5,
    "attendance_percentage": 89,
    "cgpa": 8.5,
    "pending_fees": 25000.00,
    "pending_approvals": 1,
    "unread_chats": 3,
    "next_exam": {
      "subject": "Data Structures",
      "time": "10:00 AM, Apr 15",
      "room": "Hall-A"
    }
  }
}
```

---

### GET `/students/me/dashboard/`

Student dashboard (mobile app shape).

**Response (200):**
```json
{
  "status": "success",
  "data": {
    "student": { "id": "...", "name": "John Doe", "rollNo": "20CSE101", "..." : "..." },
    "attendancePct": 89,
    "cgpa": 8.5,
    "pendingAssignments": 3,
    "todayClasses": [
      { "id": "...", "subjectId": "...", "day": "Monday", "start": "09:00", "end": "10:00", "room": "LH-1", "type": "lecture" }
    ],
    "dueFees": 25000.00,
    "unread": 5,
    "nextExam": { "id": "...", "subjectId": "...", "name": "Mid Sem", "date": "2025-04-15", "time": "10:00", "room": "Hall-A", "durationMins": 120, "type": "mid" }
  }
}
```

---

### GET `/parent/dashboard/`

Parent dashboard.

**Response (200):**
```json
{
  "status": "success",
  "data": {
    "child": { "id": "...", "name": "John Doe", "rollNo": "20CSE101", "..." : "..." },
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

### GET `/faculty/dashboard/`

Faculty dashboard.

**Response (200):**
```json
{
  "status": "success",
  "data": {
    "faculty": {
      "id": "uuid-...",
      "name": "Dr. Smith",
      "email": "smith@example.com",
      "role": "faculty",
      "avatarColor": "#673AB7"
    },
    "classCount": 4,
    "studentCount": 240,
    "todayClasses": [
      { "class": { "id": "...", "subjectCode": "CS301", "..." : "..." }, "slot": { "day": "Monday", "start": "09:00", "end": "10:00", "room": "LH-1" } }
    ],
    "pendingAssignments": 12,
    "quizCount": 5,
    "unreadNotifications": 3
  }
}
```

---

## 24. Analytics (HOD & Principal)

### HOD Endpoints (Department scope)

| Method | Path | Description |
|--------|------|-------------|
| GET | `/hod/dashboard` | HOD department dashboard |
| GET | `/hod/me` | HOD profile |
| GET | `/hod/faculty` | Department faculty list |
| GET | `/hod/faculty/{faculty_id}` | Faculty detail |
| GET | `/hod/students` | Department students |
| GET | `/hod/attendance` | Department attendance stats |

**GET `/hod/dashboard` Response (200):**
```json
{
  "status": "success",
  "data": {
    "department": "Computer Science & Engineering",
    "facultyCount": 15,
    "studentCount": 450,
    "attendancePct": 87,
    "pendingComplaints": 5,
    "upcomingExams": 3
  }
}
```

---

### Principal Endpoints (Institution scope)

| Method | Path | Description |
|--------|------|-------------|
| GET | `/principal/dashboard` | Institution-wide dashboard |
| GET | `/principal/me` | Principal profile |
| GET | `/principal/students` | All students |
| GET | `/principal/faculty` | All faculty |
| GET | `/principal/fees` | Fee collection overview |
| GET | `/principal/placements` | Placement stats |
| GET | `/principal/insights` | AI-powered insights |
| GET | `/principal/complaints` | All complaints monitor |

**GET `/principal/dashboard` Response (200):**
```json
{
  "status": "success",
  "data": {
    "totalStudents": 2500,
    "totalFaculty": 120,
    "departments": 8,
    "attendancePct": 85,
    "feeCollectionPct": 78,
    "placedStudents": 320,
    "activeComplaints": 12
  }
}
```

---

## 25. Administration

### GET `/admin/dashboard`

Admin dashboard overview.

**Response (200):**
```json
{
  "status": "success",
  "data": {
    "totalUsers": 3000,
    "activeUsers": 2850,
    "byRole": {
      "student": 2500,
      "faculty": 120,
      "parent": 300,
      "hod": 8,
      "admin": 5
    }
  }
}
```

---

### GET `/admin/users`

List managed users (paginated, searchable).

**Response item:**
```json
{
  "id": "uuid-...",
  "name": "John Doe",
  "email": "john@example.com",
  "role": "student",
  "phone": "9876543210",
  "avatarColor": "#4CAF50",
  "is_active": true,
  "active": true,
  "is_staff": false,
  "created_at": "2025-01-15T10:00:00Z"
}
```

---

### POST `/admin/users`

Create a user via admin console.

**Request:**
```json
{
  "full_name": "New Faculty",
  "email": "faculty@example.com",
  "role": "faculty",
  "password": "Faculty@123",
  "phone": "9876543210",
  "is_active": true
}
```

---

### PATCH `/admin/users/{id}`

Update user fields.

**Request:**
```json
{
  "role": "hod",
  "is_active": true
}
```

---

### PUT `/admin/users/{id}/role`

Set a user's role.

**Request:**
```json
{ "role": "faculty" }
```

---

### PUT `/admin/users/{id}/active`

Toggle user active status.

**Request:**
```json
{ "active": false }
```

---

### GET `/admin/audit-logs`

Paginated audit trail.

**Response item:**
```json
{
  "id": "uuid-...",
  "action": "create",
  "entity": "Student",
  "entity_id": "uuid-...",
  "changes": { "roll_no": "20CSE101", "name": "John Doe" },
  "actor": "uuid-admin",
  "actorName": "Admin User",
  "actorEmail": "admin@example.com",
  "ip": "192.168.1.10",
  "at": "2025-03-20T12:00:00Z"
}
```

---

### GET `/admin/roles`

List all available roles.

**Response (200):**
```json
{
  "status": "success",
  "data": [
    { "value": "super_admin", "label": "Super Admin" },
    { "value": "admin", "label": "Admin" },
    { "value": "principal", "label": "Principal" },
    { "value": "hod", "label": "HOD" },
    { "value": "faculty", "label": "Faculty" },
    { "value": "parent", "label": "Parent" },
    { "value": "student", "label": "Student" }
  ]
}
```

---

### GET `/admin/permissions`

List role-permission matrix.

---

## Error Response Format

All errors follow the envelope pattern:

```json
{
  "status": "error",
  "data": {
    "detail": "Authentication credentials were not provided."
  }
}
```

**Validation errors:**
```json
{
  "status": "error",
  "data": {
    "email": ["A user with this email already exists."],
    "password": ["This password is too common."]
  }
}
```

---

## Common HTTP Status Codes

| Code | Meaning |
|------|---------|
| 200 | Success |
| 201 | Created |
| 400 | Validation error |
| 401 | Unauthenticated |
| 403 | Forbidden (wrong role/scope) |
| 404 | Not found |
| 429 | Rate limited |

---

## Rate Limits

| Endpoint | Limit |
|----------|-------|
| `/auth/login` | 5 requests/minute |
| `/auth/forgot-password` | 3 requests/minute |
| All other endpoints | No hard throttle |

---

## OpenAPI / Swagger

- Swagger UI: `GET /api/schema/swagger-ui/`
- ReDoc: `GET /api/schema/redoc/`
- Raw schema: `GET /api/schema/`
- Health check: `GET /health/` → `{ "status": "ok" }`
