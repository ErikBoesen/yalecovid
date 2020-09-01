from flask import Flask
from config import Config
from celery import Celery
from flask_redis import FlaskRedis
from flask_cors import CORS


app = Flask(__name__)
app.config.from_object(Config)
celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
celery.conf.update(app.config)
redis = FlaskRedis(app, decode_responses=True)
cors = CORS(app)

from app import routes, errors, api
app.register_blueprint(api.api_bp, url_prefix='/api')
