from flask import render_template
from app import app, db


COLORS = {
    'green': '',
    'yellow': 'ffeb3b',
    'orange': 'ff5722',
    'red': 'f40707',
}


@app.route('/')
def index():
    color = 'yellow'
    return render_template('index.html', color=COLORS[color])
