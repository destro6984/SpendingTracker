from spendingtracker import app


@app.route('/')
@app.route('/home')
def hello_world():
    return 'Hello, World!'