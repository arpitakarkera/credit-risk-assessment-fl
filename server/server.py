import engineio
import eventlet
import socketio
import retry
import pandas as pd

sio = socketio.Server(async_mode='eventlet')
app = socketio.Middleware(sio)

@sio.on('connect')
def connect(sid, environ):
    print('connect')
    sio.emit('my message', {'data': 'foobar'})

@sio.on('message')
def message(sid, data):
    print('message ', data)

@sio.on('disconnect')
def disconnect(sid):
    print('disconnect ', sid)

@sio.on('send_model_updates')
def send_model_updates(sid, updates_json):
    print('model updates received from ', sid)
    print(updates_json)
    sio.emit('dummy', '{"structure" : ' + retry.model_json + ', "weights" : ' + retry.model_weights_json + '}')

def connServ():
  eventlet.wsgi.server(eventlet.listen(('127.0.0.1', 8000)), app)

def emitServ():
  eventlet.greenthread.sleep(seconds=5)
  sio.emit('send_model', '{"structure" : ' + retry.model_json + ', "weights" : ' + retry.model_weights_json + '}')
  sio.emit('message', 'hello')
  # eventlet.greenthread.sleep(seconds=5)
  # sio.emit('send_weights', retry.model_weights_json)

if __name__ == '__main__':
  pool = eventlet.GreenPool()
  pool.spawn(connServ)
  pool.spawn(emitServ)
  pool.waitall()
