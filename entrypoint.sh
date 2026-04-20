#!/bin/sh
set -e

echo "Starting Django entrypoint script..."

# 1. Wait for database (only if DB_HOST is set)
if [ -n "$DB_HOST" ]; then
  echo "Waiting for database at $DB_HOST:$DB_PORT..."
  # Try to wait for the database to be ready
  # If 'nc' is available (installed in Dockerfile), we can use it
  if command -v nc >/dev/null 2>&1; then
    while ! nc -z "$DB_HOST" "${DB_PORT:-5432}"; do
      sleep 1
    done
    echo "Database is ready!"
  else
    echo "Waiting 5 seconds for database..."
    sleep 5
  fi
fi

# 2. Apply database migrations
echo "Running migrations..."
python manage.py migrate --noinput

# 3. Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput --clear

# 4. Create superuser only if credentials are provided
# 4. Create superuser only if credentials are provided
if [ -n "$DJANGO_SUPERUSER_EMAIL" ] && [ -n "$DJANGO_SUPERUSER_PASSWORD" ]; then
  echo "Attempting to create superuser ($DJANGO_SUPERUSER_EMAIL)..."
  python manage.py createsuperuser --noinput 2>&1 || echo "Superuser creation skipped (likely already exists)."
else
  echo "Skipping superuser creation - DJANGO_SUPERUSER_EMAIL or DJANGO_SUPERUSER_PASSWORD not provided"
fi

echo "Entrypoint script completed successfully!"

# 5. Execute the CMD from Dockerfile
exec "$@"