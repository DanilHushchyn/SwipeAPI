MANAGE = python manage.py

run:
	$(MANAGE) runserver

migrations:
	$(MANAGE) makemigrations

migrate:
	$(MANAGE) migrate

superuser:
	$(MANAGE) createsuperuser

worker:
	celery -A SwipeAPI worker -l info

dumpdata:
	$(MANAGE) dumpdata  -e contenttypes -e auth.Permission > db.json

startapp:
	$(MANAGE) migrate --no-input
	$(MANAGE) loaddata db.json
	$(MANAGE) collectstatic --no-input
	gunicorn SwipeAPI.wsgi:application --bind 0.0.0.0:8000
