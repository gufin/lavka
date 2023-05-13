#!/bin/sh

# Wait for the database to start
echo "Waiting for database to start..."
while ! nc -z db 5432; do
  sleep 1
done

echo "Database started"

# Apply database migrations
/app/bin/alembic upgrade head

# Run the main application
exec "$@"
