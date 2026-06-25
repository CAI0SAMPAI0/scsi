#!/bin/bash
set -e
python manage.py migrate --noinput
python manage.py collectstatic --noinput 2>/dev/null
WORKERS=${GUNICORN_WORKERS:-1}
exec gunicorn core.wsgi:application --bind 0.0.0.0:7860 --workers $WORKERS --timeout 120
