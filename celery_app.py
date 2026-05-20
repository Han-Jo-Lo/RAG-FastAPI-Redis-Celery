from celery import Celery
import os

app_celery=Celery(
    'worker',
    backend=os.getenv('CELERY_BACKEND_URL'),
    broker=os.getenv('CELERY_BROKER_URL'),
    include=['tasks','process_doc']
)