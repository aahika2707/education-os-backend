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

python manage.py migrate --noinput
python manage.py collectstatic --noinput

# Optionally create an admin user from env on first boot (dev convenience).
# Set DJANGO_CREATE_SUPERUSER=true plus DJANGO_SUPERUSER_USERNAME/EMAIL/PASSWORD.
if [ "$DJANGO_CREATE_SUPERUSER" = "true" ]; then
  echo "Ensuring superuser '$DJANGO_SUPERUSER_USERNAME' exists ..."
  python manage.py createsuperuser --noinput 2>/dev/null || true
fi

exec "$@"
