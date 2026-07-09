# education-os

A Django project with basic CRUD for **Courses**, fully dockerized with Postgres,
gunicorn, and WhiteNoise.

## Stack

- Django 5.2 (LTS)
- PostgreSQL 16
- gunicorn (WSGI server)
- WhiteNoise (static file serving)
- Docker + Docker Compose

## Quick start

```bash
cp .env.example .env        # optional; sensible defaults are baked in
docker compose up --build
```

Then open:

| URL | What |
| --- | --- |
| http://localhost:8000/           | Courses list (CRUD UI) |
| http://localhost:8000/courses/new/ | Create a course |
| http://localhost:8000/admin/     | Django admin (login `admin` / `admin`) |

The web container automatically waits for Postgres, runs migrations, collects
static files, and (in dev) creates the `admin` superuser.

## CRUD

The `courses` app exposes full CRUD via class-based views + templates:

| Action | URL | View |
| --- | --- | --- |
| List   | `/courses/`               | `CourseListView` |
| Create | `/courses/new/`           | `CourseCreateView` |
| Read   | `/courses/<id>/`          | `CourseDetailView` |
| Update | `/courses/<id>/edit/`     | `CourseUpdateView` |
| Delete | `/courses/<id>/delete/`   | `CourseDeleteView` |

## Common commands

```bash
# Run the test suite
docker compose run --rm web python manage.py test

# Make migrations after changing models.py
docker compose run --rm web python manage.py makemigrations

# Open a shell
docker compose run --rm web python manage.py shell

# Stop and wipe the database volume
docker compose down -v
```

## Local (non-Docker) development

Requires Python 3.10+. With no `POSTGRES_DB` set, the app falls back to SQLite.

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

## Production notes

- Set a strong `DJANGO_SECRET_KEY` and `DJANGO_DEBUG=False`.
- Set `DJANGO_ALLOWED_HOSTS` to your domain(s).
- Disable `DJANGO_CREATE_SUPERUSER` and rotate the admin password.
- Put the app behind a TLS-terminating reverse proxy and set
  `DJANGO_SECURE_COOKIES=true`.
