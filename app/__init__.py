from flask import Flask
from config import Config
from celery import Celery

app = Flask(__name__)
app.config.from_object(Config)
celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])

from app import routes, errors, api
app.register_blueprint(api.api_blueprint, url_prefix='/api')
