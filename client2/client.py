import socketio
import json
import pyDHE
import time
from pymemcache.client import base


#import logging as log
from secure_aggregation import SecureAggregation
from flclient import FLClient
from keras import backend as K
from keras.models import model_from_json
import tensorflow as tf

sio = socketio.Client()

fl_client = None
sa_client = SecureAggregation()
mem_client = base.Client(('localhost', 11211))
mem_client.set('connection',"Connection not established")
mem_client.set('model_parameters',"Waiting for others to connect")
mem_client.set('training_status',"Training Received Model on Local Data")
mem_client.set('updates_status',"Federated Averaging in Process")
mem_client.set('clear_round_success','Server averaging the updates')
mem_client.set('username',"")
mem_client.set('password',"")
mem_client.set('model','')

var = 0
Alice = None
pkey = None
credentials = {}
updates = []
iter = 0


@sio.on('connect')
def on_connect():
	global Alice, pkey, Alice_server, pkey_server, credentials

	Alice = pyDHE.new()
	pkey = Alice.getPublicKey()
	while not mem_client.get('username') or not mem_client.get('password'):
		time.sleep(5)
		#continue
	print(' connection established ')
	credentials['username'] = mem_client.get('username').decode('utf-8')
	credentials['password'] = mem_client.get('password').decode('utf-8')
	sio.emit('authenticate', credentials)
	mem_client.set('connection',"Connection Successfully Established")
	#mem_client.set('connection',"Connection Successfully Established")


@sio.on('receive_averaged_model')
def receive_averaged_model(model_string):
	mem_client.set('model',model_string)
	sio.emit('disconnect')

@sio.on('message')
def on_message(data):
	print(' data received at client ' + data)
	sio.emit('message','This message has been successfully received')
	#fl_client.process_message(data)

@sio.on('disconnect')
def on_disconnect():
	global credentials
	credentials['username'] = None
	credentials['password'] = None
	mem_client.set('connection',"Connection not established")
	mem_client.set('model_parameters',"Waiting for model to be received")
	mem_client.set('training_status',"Training Received Model on Local Data")
	mem_client.set('updates_status',"Federated Averaging in Process")
	mem_client.set('clear_round_success','Server averaging the updates')
	print(' disconnected from server ')

@sio.on('send_perturbs')
def on_send_perturbs(data):
	global updates
	print(data)
	while not updates:
		time.sleep(5)
	suv_dict = sa_client.encryption(updates)
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
@sio.on('wait_shared_key')
def on_wait_shared_key(data):

	skey = sa_client.get_shared_key_length()
	while(skey < data):
		time.sleep(5)
		skey = sa_client.get_shared_key_length()

@sio.on('receive_pub_keys')
def receive_pub_keys(pub_keys):
	global Alice
	print("Received public keys")
	tf = False
	tf = sa_client.receive_pub_keys(pub_keys,Alice)
	#while not tf:
	#	time.sleep(5)
	#tf = False
	sio.emit('shared_key_status','shared keys made')

@sio.on('get_public_keys')
def on_get_public_keys(data):
	global pkey
	#print("PUBLIC KEY")
	#print(pkey)
	sio.emit('receive_public_key',pkey)

@sio.on('clear_round')
def on_clear_round(data):
	global updates
	updates = []
	sa_client.deleteVal()

	mem_client.set('model_parameters',"Waiting for model to be received")
	mem_client.set('training_status',"Training Received Model on Local Data")
	mem_client.set('updates_status',"Federated Averaging in Process")


	mem_client.set('clear_round_success','Round completed')


@sio.on('receive_model')
def on_receive_model(model_json):
	global updates, count, iter
	print('message received with ', model_json)
	mem_client.set('model_parameters',"Model downloaded successfully")
	iter += 1
	fl_client = FLClient(iter)
	#count = fl_client.return_count()
	dict = json.loads(model_json)
	model = model_from_json(json.dumps(dict["structure"]))
	fl_client.set_model(model)
	model_weights = fl_client.weights_from_json(json.dumps(dict["weights"]))
	fl_client.set_weights(model_weights)
	updates = fl_client.train_model(model_weights)
	mem_client.set('training_status',"Training completed successfully")
	sio.emit('training_status','training done')
	#updates_json = fl_client.get_updates_json(model_weights)

	print(' sending updates to server ')
	K.clear_session()
	#sio.emit('send_model_updates', updates_json)

		#sio.emit('message','This message has been successfully received')


@sio.on('receive_suvs')
def on_receive_suvs(encrypted_suv_clientwise):
	sa_client.decryption(encrypted_suv_clientwise)
	sio.emit('get_updates', sa_client.create_update())
	mem_client.set('updates_status',"Updates sent back to server successfully")


sio.connect('http://192.168.43.248:8004')
