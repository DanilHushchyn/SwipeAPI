import os

from celery import Celery
from celery.schedules import crontab

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'SwipeAPI.settings')

app = Celery('SwipeAPI')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django apps.
app.autodiscover_tasks()

app.conf.beat_schedule = {
    'manage_subscription_every_day': {
        'task': 'client.tasks.subscriptions',
        'schedule': crontab(),  # change to `crontab(minute=0, hour=0)` if you want it to run daily
        # at midnight
    },
    'check_deactivating_promotion_every_day': {
        'task': 'client.tasks.deactivate_promotions',
        'schedule': crontab(),  # change to `crontab(minute=0, hour=0)` if you want it to run daily
        # at midnight
    },
}
app.conf.timezone = 'Europe/Kiev'
