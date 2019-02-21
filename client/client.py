import socketio
from flclient import FLClient

import json
import numpy as np
from keras.models import model_from_json
import tensorflow as tf

def weights_from_json(model_weights_json):
	json_load = json.loads(model_weights_json)
	model_weights_list = np.array(json_load)
	model_weights = []
	for i in model_weights_list:
		model_weights.append(np.array(i,dtype=np.float32))
	return model_weights

sio = socketio.Client()

fl_client = FLClient()

@sio.on('connect')
def on_connect():
	print(' connection established ')

@sio.on('message')
def on_message(data):
	print(' data received at client ')
	global fl_client
	fl_client.process_message(data)

@sio.on('disconnect')
def on_disconnect():
    print(' disconnected from server ')

@sio.on('send_model')
def on_send_model(model_json):
	print(' model received ')
	dict = json.loads(model_json)
	model = model_from_json(json.dumps(dict["structure"]))
	fl_client.set_model(model)
	model_weights = weights_from_json(json.dumps(dict["weights"]))
	fl_client.set_weights(model_weights)
	fl_client.train_model()
	updates_json = fl_client.get_updates_json(model_weights)
	print(' sending updates to server ')
	sio.emit('send_model_updates', updates_json)

@sio.on('dummy')
def on_dummy(model_json):
	print(' model received ')
	dict = json.loads(model_json)
	model = model_from_json(json.dumps(dict["structure"]))
	fl_client.set_model(model)
	model_weights = weights_from_json(json.dumps(dict["weights"]))
	fl_client.set_weights(model_weights)
	fl_client.train_model()
	updates_json = fl_client.get_updates_json(model_weights)
	# print(' sending updates to server ')
	# sio.emit('send_model_updates', updates_json)

# @sio.on('send_weights')
# def on_send_weights(model_weights_json):
# 	print(' model weights received ')
# 	global fl_client
# 	model_weights = weights_from_json(model_weights_json)
# 	# print(model_weights)
# 	global model
# 	fl_client.set_weights(model_weights)


sio.connect('http://localhost:8000')
