import sqlite3
from flask import Flask, render_template
app = Flask(__name__)

SQL = {}
SQL['getQueue'] = "select bnet from processQueue"
SQL['isQueued'] = "select count(1) from processQueue where bnet='{bnet}'"
SQL['enqueue'] = "INSERT INTO processQueue (`bnet`) VALUES ('{bnet}')"


@app.route('/')
def hello_world():
    return render_template('build.html')


@app.route('/queue/')
@app.route('/queue/<string:bnetId>')
def show_post(bnetId=None):
    global SQL
    addedToQueue = False
    conn = sqlite3.connect('d3.db')
    if (bnetId is not None):
        cursor = conn.execute(SQL['isQueued'].format(bnet=bnetId))
        data = cursor.fetchone()
        if (data[0] == 0):
            conn.execute(SQL['enqueue'].format(bnet=bnetId))
            conn.commit()
            addedToQueue = True

    rows = conn.execute(SQL['getQueue'])
    queue = rows.fetchall()
    conn.close()

    return render_template('queue.html', bnetId=bnetId, queue=queue, addedToQueue=addedToQueue)


@app.route('/profile/')
@app.route('/profile/<string:bnetId>')
def show_test():
    return render_template('test.html')
