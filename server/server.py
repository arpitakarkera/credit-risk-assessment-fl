import engineio
import eventlet
import socketio

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

def connServ():
  eventlet.wsgi.server(eventlet.listen(('127.0.0.1', 8000)), app)

def emitServ():
  eventlet.greenthread.sleep(seconds=5)
  sio.emit('message','hello')

if __name__ == '__main__':
  pool = eventlet.GreenPool()
  pool.spawn(connServ)
  pool.spawn(emitServ)
  pool.waitall()
