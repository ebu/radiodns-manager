#!/usr/bin/env bash
python wait_db.py
python manage.py migrate --noinput &&
python manage.py collectstatic --noinput &&
python manage.py create_ecc_records &&
python manage.py create_language_records &&
python manage.py initadmin &&
uwsgi radiodns.ini
