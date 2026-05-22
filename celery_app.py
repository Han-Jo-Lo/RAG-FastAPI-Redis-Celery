from celery import Celery
import os
from dotenv import load_dotenv
load_dotenv()

app_celery=Celery(
    'worker',
    backend=os.getenv('CELERY_BACKEND_URL'),
    broker=os.getenv('CELERY_BROKER_URL'),
    include=['tasks','process_doc']
)

app_celery.conf.update(
    result_backend=os.getenv('CELERY_BACKEND_URL'),
    task_track_started=True, # Para que veas el estado 'STARTED' en lugar de solo PENDING
    timezone='UTC'
)