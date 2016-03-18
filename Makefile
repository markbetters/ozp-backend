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
	python manage.py test

ftest: pre
	python manage.py test

run:
	python manage.py runserver

runp:
	gunicorn --workers=`nproc` ozp.wsgi -b localhost:8000 --access-logfile logs.txt --error-logfile logs.txt -p gunicorn.pid

dev: clean pre create_static
	python manage.py makemigrations ozpcenter
	python manage.py makemigrations ozpiwc
	python manage.py migrate

	echo 'Loading sample data...'
	python manage.py runscript sample_data_generator

	python manage.py runserver
