from flask import Flask
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

from app import routes, errors, api
app.register_blueprint(api.api_blueprint, url_prefix='/api')
