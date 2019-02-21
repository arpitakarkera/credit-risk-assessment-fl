import socketio
import json
import pyDHE
#import logging as log
from flclient import FLClient

sio = socketio.Client()

fl_client = FLClient()
var = 0
Alice = None
pkey = None

@sio.on('connect')
def on_connect():
	global Alice, pkey
	print(' connection established ')
	Alice = pyDHE.new()
	pkey = Alice.getPublicKey()

@sio.on('message')
def on_message(data):
	print(' data received at client ' + data)
	sio.emit('message','This message has been successfully received')
	#fl_client.process_message(data)

@sio.on('disconnect')
def on_disconnect():
    print(' disconnected from server ')

@sio.on('send_perturbs')
def on_send_perturbs(data):
	print(data)
	suv_dict = fl_client.encryption()
	#print("SUV DICT AFTER ENCRYPTION:")
	#print(suv_dict)
	#print (suv_dict)
	sio.emit('receive_perturb',suv_dict)

'''
@sio.on('send_model')
def on_send_model(model):
	print(' model received ')
	#fl_client.train_model(model)
'''
'''
@sio.on('receive_diffie_params')
def receive_diffie_params(data):
	global var
	print('inside diffie params')
	var = fl_client.generate_public_key(data)
	print("Generated public key")
	print(var)
	sio.emit('receive_public_key',var)

@sio.on('receive_pub_keys')
def receive_pub_keys(pub_keys):
	#fl_client.receive_pub_keys(pub_keys)
'''
@sio.on('receive_pub_keys')
def receive_pub_keys(pub_keys):
	global Alice
	print("Received public keys")
	fl_client.receive_pub_keys(pub_keys,Alice)

@sio.on('get_public_keys')
def on_get_public_keys(data):
	global pkey
	#print("PUBLIC KEY")
	#print(pkey)
	sio.emit('receive_public_key',pkey)

@sio.on('clear_round')
def on_clear_round(data):
	fl_client.deleteVal()

@sio.on('receive_model')
def on_receive_model(data):
	print('message received with ', data)
	if fl_client.train_model(data):
		print("train =True")
		sio.emit('train_status')
		#sio.emit('message','This message has been successfully received')


@sio.on('receive_suvs')
def on_receive_suvs(encrypted_suv_clientwise):
	fl_client.decryption(encrypted_suv_clientwise)
	sio.emit('get_updates', fl_client.create_update())

sio.connect('http://0.0.0.0:8003')
