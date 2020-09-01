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
    color = redis.get('color')
    yale = json.loads(redis.get('yale'))
    connecticut = json.loads(redis.get('connecticut'))
    return render_template('index.html', theme_color=COLORS[color], color=color, data=yale)
