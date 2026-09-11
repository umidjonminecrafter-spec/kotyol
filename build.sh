#!/usr/bin/env bash
# exit on error
set -o errexit

pip install -r requirements.txt
python -m core.fix_migrations || true
python manage.py migrate --noinput
python manage.py collectstatic --noinput --clear || true
