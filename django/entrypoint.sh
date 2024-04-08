#!/bin/sh
#python manage.py makemigrations --noinput
#python manage.py migrate --noinput
gunicorn config.wsgi:application --workers 4 --bind 0.0.0.0:8000
# gunicorn for nginx
# gunicorn --workers 5 --bind unix:/ded-pyhto.sock config.wsgi:application
# python manage.py runserver 0.0.0.0:8000
