from flask import Flask
import sys
import signal

app = Flask(__name__)


@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"


def cleanup(signal, frame):
    print('Closing API...')
    sys.exit(0)


signal.signal(signal.SIGINT, cleanup)
signal.pause()
