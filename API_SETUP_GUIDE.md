# AI Campus OS - API Setup & Testing Guide

## Prerequisites

- Python 3.9+
- All dependencies installed: `pip install -r requirements.txt`

---

## Step 1: Run Migrations

```powershell
$env:DJANGO_SETTINGS_MODULE="config.settings"
python manage.py migrate
```

---

## Step 2: Create Superuser (Admin)

```powershell
$env:DJANGO_SUPERUSER_PASSWORD="Admin@123"
python manage.py createsuperuser --email admin@example.com --full_name "Admin User" --noinput
```

Credentials:
- Email: `admin@example.com`
- Password: `Admin@123`

---

## Step 3: Start the Server

```powershell
python manage.py runserver
```

Server runs at: `http://127.0.0.1:8000`

Swagger UI: `http://127.0.0.1:8000/api/schema/swagger-ui/`

---

## Step 4: Login as Admin

```bash
curl -X POST http://127.0.0.1:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@example.com", "password": "Admin@123"}'
```

Response:
```json
{
  "status": "success",
  "data": {
    "user": {"id": "...", "name": "Admin User", "email": "admin@example.com", "role": "super_admin"},
    "access_token": "eyJ...",
    "refresh_token": "eyJ...",
    "active_role": "super_admin"
  }
}
```

**Copy the `access_token` — you need it for all authenticated requests.**

---

## Step 5: Register a New User (Admin Only)

```bash
curl -X POST http://127.0.0.1:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <ACCESS_TOKEN>" \
  -d '{
    "email": "aashika2707@gmail.com",
    "full_name": "Ashika",
    "role": "student",
    "password": "aashika2707#",
    "phone": "9384398392"
  }'
```

Available roles: `super_admin`, `admin`, `principal`, `hod`, `faculty`, `parent`, `student`

---

## Step 6: Login as the New User

```bash
curl -X POST http://127.0.0.1:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "aashika2707@gmail.com", "password": "aashika2707#"}'
```

---

## All Auth Endpoints

| Method | Endpoint | Auth Required | Description |
|--------|----------|:---:|-------------|
| POST | `/api/v1/auth/login` | No | Login (email/phone + password) |
| POST | `/api/v1/auth/refresh` | No | Get new access token using refresh token |
| POST | `/api/v1/auth/logout` | Yes | Blacklist refresh token |
| GET | `/api/v1/auth/me` | Yes | Get current user info |
| GET | `/api/v1/auth/roles/{user_id}` | Yes | List roles a user can switch to |
| POST | `/api/v1/auth/switch-role` | Yes | Switch active role |
| POST | `/api/v1/auth/change-password` | Yes | Change own password |
| POST | `/api/v1/auth/forgot-password` | No | Request password reset OTP |
| POST | `/api/v1/auth/reset-password` | No | Reset password with OTP code |
| POST | `/api/v1/auth/register` | Yes (Admin) | Create new user |

---

## How Auth Works

1. All protected endpoints need: `Authorization: Bearer <access_token>`
2. Access token expires in **30 minutes**
3. Use the refresh token to get a new access token (without re-login)
4. On logout, the refresh token is blacklisted (can't be reused)

---

## Refresh Token Usage

When access token expires:
```bash
curl -X POST http://127.0.0.1:8000/api/v1/auth/refresh \
  -H "Content-Type: application/json" \
  -d '{"refresh": "<REFRESH_TOKEN>"}'
```

---

## Change Password

```bash
curl -X POST http://127.0.0.1:8000/api/v1/auth/change-password \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <ACCESS_TOKEN>" \
  -d '{"current_password": "oldpass", "new_password": "NewStr0ng!Pass"}'
```

---

## Forgot Password (OTP Flow)

**Request OTP:**
```bash
curl -X POST http://127.0.0.1:8000/api/v1/auth/forgot-password \
  -H "Content-Type: application/json" \
  -d '{"email": "aashika2707@gmail.com"}'
```

**Reset with OTP code:**
```bash
curl -X POST http://127.0.0.1:8000/api/v1/auth/reset-password \
  -H "Content-Type: application/json" \
  -d '{"email": "aashika2707@gmail.com", "code": "123456", "new_password": "NewStr0ng!Pass"}'
```

---

## Running Tests

```powershell
$env:DJANGO_SETTINGS_MODULE="config.settings"
$env:CELERY_TASK_ALWAYS_EAGER="True"
python manage.py test accounts --verbosity=2
```

---

## Important Notes

- **No self-registration** — Only admins can create users
- **JWT-based** — Use `Authorization: Bearer <token>`, not CSRF tokens
- **CSRF token in Swagger UI** is auto-handled, no need to copy it manually
- **Rate limits**: Login = 5/min, Password reset = 3/min
