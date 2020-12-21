#!/bin/sh

python manage.py makemigrations
python manage.py migrate
python manage.py init_data
python manage.py crontab add
python manage.py crontab show
#python manage.py runserver 0.0.0.0:8000
exec gunicorn covid_api.wsgi --workers 3 --timeout 600 --bind 0.0.0.0:8000
