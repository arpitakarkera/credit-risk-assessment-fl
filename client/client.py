import socketio
#import logging as log
from flclient import FLClient

sio = socketio.Client()

fl_client = FLClient()

@sio.on('connect')
def on_connect():
	print(' connection established ')

@sio.on('message')
def on_message(data):
	print(' data received at client ')
	fl_client.process_message(data)

@sio.on('disconnect')
def on_disconnect():
    print(' disconnected from server ')

@sio.on('send_model')
def on_send_model(model):
	print(' model received ')
	fl_client.train_model(model)

sio.connect('http://127.0.0.1:8000')
