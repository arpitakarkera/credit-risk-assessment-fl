import socketio

sio = socketio.Client()

@sio.on('connect')
def on_connect():
	print('connection established')

@sio.on('my message')
def on_message(data):
    print('message received with ', data)
    sio.emit('my message', {'response1': 'my response'})

@sio.on('disconnect')
def on_disconnect():
    print('disconnected from server')

sio.connect('http://192.168.43.17:8000')
#sio.wait()