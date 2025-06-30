#!/bin/sh

# Wait for PostgreSQL to be ready
echo "Waiting for PostgreSQL..."

while ! nc -z $DB_HOST $DB_PORT; do
  sleep 1
done

echo "PostgreSQL started"

# Apply database migrations
python manage.py migrate

# Collect static files (optional, if your project uses static files)
# python manage.py collectstatic --noinput

# Start the Django server
exec "$@"
