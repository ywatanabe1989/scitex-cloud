#!/bin/bash
set -e

# Install scitex package (editable mode)
if [ -d "/scitex-code" ]; then
    echo "Installing scitex package..."
    pip install --user -e /scitex-code
    echo "Scitex package installed!"
fi

# Wait for database to be ready
echo "Waiting for database..."
while ! nc -z db 5432; do
  sleep 0.1
done
echo "Database is ready!"

# Run migrations
echo "Running migrations..."
python manage.py migrate --noinput

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Starting application..."
exec "$@"
