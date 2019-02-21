import engineio
import eventlet
eventlet.monkey_patch()
import socketio
import time
import json
import numpy as np
import pyDHE

from flserver import FLServer

sio = socketio.Server(async_mode='eventlet')
app = socketio.Middleware(sio)
count_clients = 0
conn_threshold  = 3
update_threshold = 3
updates_received = 0
client_updates = {}
server_wait_time = 5
suv_dictionary = {}


fl_server = FLServer()

diffie_parameters = fl_server.diffie_parameters()
pub_keys = {}

@sio.on('connect')
def connect(sid, environ):
    global count_clients
    count_clients+=1
    print('connect')
    client_updates[sid] = 0

  #sio.emit('my message', {'data': 'foobar'})

@sio.on('message')
def message(sid, data):
    print('message ', data)

@sio.on('disconnect')
def disconnect(sid):
    global count_clients
    count_clients-=1
    client_updates.pop(sid)
    print('disconnect ', sid)

@sio.on('get_updates')
def get_updates(sid, update):
    global updates_received, client_updates
    updates_received += 1
    update = np.array(update)
    client_updates[sid] = update

@sio.on('receive_public_key')
def receive_public_key(sid, data):
    #print("Insideeeeeeee")
    global pub_keys
    pub_keys[sid] = data
    '''print("received pub key:")
    print(data)
    print("pub key dictionary")
    print(pub_keys)'''


@sio.on('receive_perturb')
def receive_perturb(sid,suv_dict):
    global suv_dictionary
    #suv_dict = json.loads(jsonified_dict)
    suv_dictionary[sid] = suv_dict
    #print("PRINTING SUV DICTIONARY ON SERVER")
    #print(suv_dictionary)

@sio.on('train_status')
def train_status(sid):
    print("Inside train_status")
    #print("train status: " + data)
    #secure_agg()

def connServ():
    eventlet.wsgi.server(eventlet.listen(('', 8003)), app)

'''
def emitServ():
  while True:
    eventlet.greenthread.sleep(seconds=5)
    sio.emit('my message','hello')
'''

def send_model():
    global count_clients, conn_threshold
    if count_clients >= conn_threshold :
        print('threshold reached')
        model_parameters = fl_server.pass_model_parameters()
        #sio.emit('message','server sent you data')
        sio.emit('receive_model', model_parameters)
        secure_agg()
        return True
    return False

def diffie_hellman():
    '''global pub_keys, diffie_parameters
    sio.emit('receive_diffie_params', diffie_parameters)
    while len(pub_keys)<count_clients:
        eventlet.greenthread.sleep(seconds=5)
    #print (len(pub_keys))
    print("Inside Diffie Hellman printing public key dictionary")
    print (pub_keys)
    sio.emit('receive_pub_keys', pub_keys)'''
    global pub_keys
    sio.emit('get_public_keys','send me public keys')
    while len(pub_keys)<count_clients:
        eventlet.greenthread.sleep(seconds=5)
    #print("PUBLIC KEYS RECEIVED")
    #print(pub_keys)
    sio.emit('receive_pub_keys',pub_keys)
    eventlet.greenthread.sleep(seconds=5)

def secure_agg():
    global count_clients, suv_dictionary
    print("Inside secure aggregation")
    #sio.emit('message','server sent you data')
    diffie_hellman()
    sio.emit('send_perturbs','Send me the perturbations')
    while len(suv_dictionary) < count_clients:
        eventlet.greenthread.sleep(seconds=5)
    #print("PRINTING SUV DICTIONARY:")
    #print(suv_dictionary)
    #length_dict = {key: len(value) for key, value in suv_dictionary.items()}
    #print("SIZE PRINTING")
    #print(length_dict)
    encrypted_suv_clientwise = fl_server.perturb_util1(suv_dictionary)
    for key, values in encrypted_suv_clientwise.items():
        sio.emit('receive_suvs',values,room=key)



def federating_process():
  global count_clients, updates_received, update_threshold, client_updates, suv_dictionary
  while True:
    eventlet.greenthread.sleep(seconds=5)
    if  send_model():
        #secure_agg()
        eventlet.greenthread.sleep(seconds=server_wait_time)
        while updates_received < count_clients:
            eventlet.greenthread.sleep(seconds=5)
        #print("PRINTING CLIENT UPDATES:")
        #print(client_updates)
        for key, value in client_updates.items():
            if value is 0:
                sio.emit('my message','stop training. new model on the way', room=key)
        fl_server.averaging(client_updates)
        sio.emit('clear_round','Clear the round rn')
      #print (client_updates)
        for key, value in client_updates.items():
            client_updates[key] = 0
        updates_received = 0
        suv_dictionary = {}
        print("-------------------------------------------ROUND COMPLETED-----------------------------------------------------------------------------")



if __name__ == '__main__':
    pool = eventlet.GreenPool()
    pool.spawn(connServ)
    #pool.spawn(emitServ)
    pool.spawn(federating_process)
    pool.waitall()
