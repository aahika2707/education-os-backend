#!/bin/sh
set -e

# Wait for Postgres to accept connections (only when configured)
if [ -n "$POSTGRES_HOST" ]; then
  echo "Waiting for Postgres at $POSTGRES_HOST:${POSTGRES_PORT:-5432} ..."
  while ! nc -z "$POSTGRES_HOST" "${POSTGRES_PORT:-5432}"; do
    sleep 0.5
  done
  echo "Postgres is up."
fi

# Migrate/collectstatic/superuser/seed happen once per deploy from the web
# process. This same image+entrypoint also boots the Celery worker (see
# docker-compose.yml), which would otherwise race the web container on
# migrations — so we skip init only for the worker. We match on the whole
# command ($*), not $1, because the Dockerfile CMD is shell-form: Docker
# runs it as `/bin/sh -c "gunicorn ..."`, so $1 is "/bin/sh", never "gunicorn".
case "$*" in
  *"celery "*worker*|*"celery "*beat*) RUN_DB_INIT=0 ;;
  *) RUN_DB_INIT=1 ;;
esac

if [ "$RUN_DB_INIT" = "1" ]; then
  python manage.py migrate --noinput
  python manage.py collectstatic --noinput

  # Optionally create an admin user from env on first boot (dev convenience).
  # Set DJANGO_CREATE_SUPERUSER=true plus DJANGO_SUPERUSER_USERNAME/EMAIL/PASSWORD.
  if [ "$DJANGO_CREATE_SUPERUSER" = "true" ]; then
    echo "Ensuring superuser '$DJANGO_SUPERUSER_USERNAME' exists ..."
    python manage.py createsuperuser --noinput 2>/dev/null || true
  fi

  # Optional demo data (9 role logins, password campus123) so a fresh database
  # has something to log in with. Idempotent — safe to leave on, but you can
  # unset DJANGO_SEED_DEMO once you have real data.
  if [ "$DJANGO_SEED_DEMO" = "true" ]; then
    echo "Seeding demo data ..."
    python manage.py seed_demo || true
  fi
fi

exec "$@"
