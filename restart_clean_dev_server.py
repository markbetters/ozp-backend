#!/usr/bin/env bash
export DJANGO_SETTINGS_MODULE=ozpv3.settings

rm db.sqlite3
rm -r ozpcenter/migrations/*
python manage.py makemigrations ozpcenter
python manage.py migrate
# TODO: load test data
# python ozpcenter/tests/sample_data_generator.py
python manage.py runserver
