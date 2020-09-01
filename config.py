import os


REDIS = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')

class Config(object):
    REDIS_URL = REDIS

    CELERY_BROKER_URL = REDIS
    CELERY_RESULT_BACKEND = REDIS
