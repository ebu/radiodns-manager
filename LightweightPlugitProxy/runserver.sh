#!/usr/bin/env bash
source venv/bin/activate &&
python wait_db.py &&
python manage.py migrate --noinput &&
python manage.py collectstatic --noinput &&
python manage.py initadmin &&
uwsgi lpp.ini
