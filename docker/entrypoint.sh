#!/usr/bin/env bash
set -e

python manage.py migrate --noinput
python manage.py collectstatic --noinput

exec gunicorn Snippets.wsgi:application --bind 0.0.0.0:8000 --workers 3 --log-level info