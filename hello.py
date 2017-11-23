import sqlite3
from flask import Flask, render_template
app = Flask(__name__)

class SQL:
    getQueue = "select battleTag from processingQueue"
    isQueued = "select count(1) from processingQueue where battleTag='{battleTag}'"
    enqueue = "INSERT INTO processingQueue (`battleTag`) VALUES ('{battleTag}')"


@app.route('/')
def hello_world():
    return render_template('build.html')


@app.route('/queue/')
@app.route('/queue/<string:battleTag>')
def show_post(battleTag=None):
    addedToQueue = False
    conn = sqlite3.connect('d3.db')
    if (battleTag is not None):
        cursor = conn.execute(SQL.isQueued.format(battleTag=battleTag))
        data = cursor.fetchone()
        if (data[0] == 0):
            conn.execute(SQL.enqueue.format(battleTag=battleTag))
            conn.commit()
            addedToQueue = True

    rows = conn.execute(SQL.getQueue)
    queue = rows.fetchall()
    conn.close()

    return render_template('queue.html', battleTag=battleTag, queue=queue, addedToQueue=addedToQueue)


@app.route('/profile/')
@app.route('/profile/<string:battleTag>')
def show_test():
    return render_template('test.html')
