from sanic import Sanic
from endpoint import bp_micro

app = Sanic(__name__)
app.blueprint(bp_micro)

if __name__ == '__main__':
    app.run(host='0.0.0.0', workers=2, port=10020, debug=True)