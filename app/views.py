from app import app
from app import r
from app import q

from flask import render_template, request

@app.route('/')
def index():
    return "hello world"
