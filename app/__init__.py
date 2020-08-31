from flask import Flask
from config import Config
from celery import Celery
from flask_redis import FlaskRedis


app = Flask(__name__)
app.config.from_object(Config)
celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
redis_client = FlaskRedis(app)

from app import routes, errors, api
app.register_blueprint(api.api_blueprint, url_prefix='/api')
