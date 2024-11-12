import os
from celery import Celery
from dotenv import load_dotenv

load_dotenv()

celery = Celery(
    'app',
    broker=os.getenv('CELERY_BROKER_URL'),
    backend=os.getenv('CELERY_BACKEND_URL'),
    include=['app.tasks'],
)

celery.conf.broker_connection_retry_on_startup = True

celery.conf.update(
    result_expires=3600,
)

if __name__ == '__main__':
    celery.start()
