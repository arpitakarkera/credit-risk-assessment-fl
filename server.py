import engineio as eio
import eventlet
import socketio

sio = socketio.Server(async_mode='eventlet')
app = socketio.Middleware(sio)

@sio.on('connect')
def connect(sid, environ):
    print('connect')
    sio.emit('my message', {'data': 'foobar'})

@sio.on('my message')
def message(sid, data):
    print('message ', data)

@sio.on('disconnect')
def disconnect(sid):
    print('disconnect ', sid)

if __name__ == '__main__':
    eventlet.wsgi.server(eventlet.listen(('192.168.43.17', 8000)), app)
