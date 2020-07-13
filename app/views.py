from app import app
from app import r
from app import q
from app.tasks import zabanshop

from flask import render_template, request,jsonify

@app.route('/', methods=['GET','POST'])
def index():

    jobs = q.jobs
    if request.method == 'POST':
        task = q.enqueue(zabanshop)
        jobs = q.jobs
        message = q
        return render_template('home.html', message=jobs)
    else:
        return render_template('home.html')
