from app import app
from app import r
from app import q
from flask_mysqldb import MySQL
from flask import render_template, request,jsonify
import re

from app.tasks import zabanshop

mysql = MySQL(app)

app.config["MYSQL_HOST"] = "localhost"
app.config["MYSQL_USER"] = "mahdi"
app.config["MYSQL_PASSWORD"] = ""
app.config["MYSQL_DB"] = "simplecrawl"


@app.route('/', methods=['GET','POST'])
def index():
    if request.method == 'POST':
        task = q.enqueue(zabanshop, job_timeout=2500)
        return render_template('home.html')
    else:
        return render_template('home.html')


@app.route("/livesearch",methods=["POST","GET"])
def livesearch():
    searchbox = request.form.get("text")
    cursor = mysql.connection.cursor()
    query = "select * from books where name LIKE '%{}%' order by name".format(searchbox)
    cursor.execute(query)
    result = cursor.fetchall()

    data = []
    for row in result:
        if row[2] == 'None':
            data.append({'id': row[0], 'name': row[1], 'price':row[4], 'specialprice':row[3], 'img':row[5]})
        else:
            data.append({'id': row[0], 'name': row[1], 'price':row[2], 'specialprice':'0','img':row[5]})
    return jsonify(data)


@app.route('/product/<id>')
def show(id):
    if id.isnumeric():
        cursor = mysql.connection.cursor()
        query = "select * from books where id={}".format(id)
        cursor.execute(query)
        result = cursor.fetchall()
        data = []
        for row in result:
            data.append({'id':row[0], 'name':row[1], 'price':row[2], 'oldprice':row[3], 'specialprice':row[4], 'img':row[5]})
        print(len(data))
        return render_template('product.html', data=result)

    else:
        result = "404"
        return render_template('product.html', data=result)

@app.errorhandler(404)
def page_not_found(e):
    # note that we set the 404 status explicitly
    return render_template('404.html'), 301

