#!/usr/bin/env bash

# Useful for Testing ONLY, this script will:
# 	* wipe the existing database
#	* wipe all existing migrations
#	* create a fresh database with a single new migration
#	* remove and collect static files
#	* remove and collect media files
#	* run unit tests

export DJANGO_SETTINGS_MODULE=ozp.settings

#rm env/ -rf

# Create TEST PYTHON ENV

# {PYTHON_HOME}/python -m venv env
# source env/bin/activate
# pip install --upgrade pip; pip install -r requirements.txt --no-cache-dir -I
# remove existing database and all migrations
rm db.sqlite3
#rm -r ozpcenter/migrations/*
#rm -r ozpiwc/migrations/*
# create new database with a single new migration
python manage.py makemigrations ozpcenter
python manage.py makemigrations ozpiwc
python manage.py migrate
# remove old static files
rm -rf static/
mkdir -p static
# collect static files
python manage.py collectstatic --noinput
# remove old media files
rm -rf media/
mkdir -p media
# run unit tests
python manage.py test
