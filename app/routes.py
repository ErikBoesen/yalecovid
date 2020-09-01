from flask import render_template
from app import app, redis, tasks

import json

COLORS = {
    'green': '29ba3a',
    'yellow': 'ffeb3b',
    'orange': 'ff5722',
    'red': 'f40707',
}

@app.route('/')
def index():
    alert_level = redis.get('alert_level')
    yale = json.loads(redis.get('yale'))
    connecticut = json.loads(redis.get('connecticut'))
    return render_template('index.html', theme_color=COLORS[alert_level], alert_level=alert_level, data=yale)
