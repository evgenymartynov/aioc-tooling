#!/usr/bin/python

import sys
from flask import Flask, redirect, render_template
from flask.ext.socketio import SocketIO

import logtail4 as Logtail

NS = '/socket.io/chat'
STATIC_FILE = None

app = Flask(__name__)
socketio = SocketIO(app)


@app.route('/')
def main_view():
  return open(STATIC_FILE).read()

@app.route('/kappa.png')
def kappa_img():
  return open('kappa.png').read()

@app.route('/doge.gif')
def doge_img():
  return open('doge.gif').read()

@app.route('/<path:path>')
def catch_all(path):
  return redirect('http://epochfail.com/' + path)

@socketio.on('connect', namespace=NS)
def ws_connect():
  pass


def msg_callback(topic, msg):
  socketio.emit('message', {
    'topic': topic,
    'msg': msg,
  }, namespace=NS)


@app.before_first_request
def init():
  global STATIC_FILE
  STATIC_FILE = sys.argv[2]

  import threading
  t = threading.Thread(target=Logtail.main,
      args=(sys.argv[1], sys.argv[2], int(sys.argv[3]), msg_callback),
  )
  t.daemon = True
  t.start()


socketio.run(app, port=8080, host='0.0.0.0')
