#!/bin/sh

python manage.py makemigrations
python manage.py migrate
python manage.py init_data
exec gunicorn covid_api.wsgi --workers 3 --timeout 600 --bind 0.0.0.0:8000
