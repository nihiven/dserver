from flask import Flask, render_template
app = Flask(__name__)


@app.route('/')
def hello_world():
    return render_template('build.html')


@app.route('/queue/')
@app.route('/queue/<string:bnetId>')
def show_post(bnetId=None):
    if (bnetId is not None):
        print 'queue {bnetId}'.format(bnetId=bnetId)

    return render_template('queueNotice.html', bnetId=bnetId)


@app.route('/profile/')
@app.route('/profile/<string:bnetId>')
def show_test():
    return render_template('test.html')
