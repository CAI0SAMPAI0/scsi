#!/bin/bash
set -e
python manage.py migrate --noinput
python manage.py collectstatic --noinput 2>/dev/null
exec gunicorn core.wsgi:application --bind 0.0.0.0:7860 --workers 3 --timeout 120
