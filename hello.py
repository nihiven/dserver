from sql import SQL, dbConnect, dbProfileExists
from flask import Flask, render_template
app = Flask(__name__)


@app.route('/')
def hello_world():
    return render_template('build.html')


@app.route('/queue/')
@app.route('/queue/<string:battleTag>')
def show_queue(battleTag=None):
    addedToQueue = False
    conn = dbConnect()
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
def show_profile(battleTag=None):
    profiles = None
    profileExists = False
    if (battleTag is None):
        conn = dbConnect()
        cursor = conn.execute(SQL.allProfiles)
        profiles = cursor.fetchall()
        conn.close()
    else:
        profileExists = dbProfileExists(battleTag)
        if (profileExists is True):
            print 'exists'
        else:
            print 'does not exist'

    return render_template('profile.html', profiles=profiles, battleTag=battleTag, profileExists=profileExists)
