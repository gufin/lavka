#!/bin/sh

# Apply database migrations
/app/bin/alembic upgrade head

# Run the main application
exec "$@"