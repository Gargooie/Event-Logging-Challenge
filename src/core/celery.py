# Настройка периодического запуска задачи

import os
from celery import Celery
from celery.schedules import crontab
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

app = Celery('core')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

app.conf.beat_schedule = {
    'process-outbox-events': {
        'task': 'core.tasks.process_outbox_events',
        'schedule': crontab(minute='*/1'),
    },
}

app.conf.task_routes = {
    'core.tasks.process_outbox_events': {'queue': 'events'},
}