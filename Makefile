# This is a make file to help with the commands

clean:
	rm -f db.sqlite3
	rm -rf static/
	rm -rf media/
	rm -f ozp.log

create_static:
	mkdir -p static
	python manage.py collectstatic --noinput
	mkdir -p media

pre:
	export DJANGO_SETTINGS_MODULE=ozp.settings

test: clean pre create_static
	python -q -X faulthandler manage.py test

softtest: pre
	python -q -X faulthandler manage.py test

install_git_hooks:
	cp .hooks/pre-commit .git/hooks/

run:
	python manage.py runserver

runp:
	gunicorn --workers=`nproc` ozp.wsgi -b localhost:8000 --access-logfile logs.txt --error-logfile logs.txt -p gunicorn.pid

codecheck:
	flake8 ozp ozpcenter ozpiwc plugins plugins_util --ignore=E501,E123,E128,E121,E124,E711,E402 --show-source

autopep:
	autopep8 ozp ozpcenter ozpiwc plugins plugins_util --ignore=E501,E123,E128,E121,E124,E711,E402 --recursive --in-place

autopepdiff:
	autopep8 ozp ozpcenter ozpiwc plugins plugins_util --ignore=E501,E123,E128,E121,E124,E711,E402 --recursive --diff

reindex_es:
	python manage.py runscript reindex_es

recommend:
	RECOMMENDATION_ENGINE='custom' python manage.py runscript recommend

recommend_es_user:
	ES_ENABLED=TRUE RECOMMENDATION_ENGINE='elasticsearch_user_base' python manage.py runscript recommend

recommend_es_content:
	ES_ENABLED=TRUE RECOMMENDATION_ENGINE='elasticsearch_content_base' python manage.py runscript recommend

dev: clean pre create_static
	python manage.py makemigrations ozpcenter
	python manage.py makemigrations ozpiwc
	python manage.py migrate

	echo 'Loading sample data...'
	python manage.py runscript sample_data_generator
	#python manage.py runscript notification_migrate  # Temp Solution - Once notifications is completely refactored, remove this line

	python manage.py runserver
