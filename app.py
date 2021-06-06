from signal import signal, SIGINT
from sys import exit

from flask import Flask

app = Flask(__name__)


@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"


def cleanup(signal, frame):
    print('Closing API...')
    exit(0)


signal(SIGINT, cleanup)
