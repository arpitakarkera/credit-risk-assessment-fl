import engineio
import eventlet
eventlet.monkey_patch()
import socketio
import time
import json
import numpy as np
import pyDHE
import retry
from flserver import FLServer
import pandas as pd
from keras.models import model_from_json

sio = socketio.Server(async_mode='eventlet')
app = socketio.Middleware(sio)

Bob = pyDHE.new(18)
pkey = Bob.getPublicKey()

count_clients = 0
count_rounds = 0
count_auth_clients = 0
conn_threshold  = 3
update_threshold = 3
updates_received = 0
client_updates = {}
server_wait_time = 5
suv_dictionary = {}
count_train_done = 0
count_shared_done = 0
fin_weights_str = retry.model_weights_json
fin_struct = retry.model_json

fin_weights = []
credentials=[{'username':'$un@in@','password':'passit'},{'username':'priya','password':'priy@'}]
shared_keys = {}
fl_server = FLServer()

pub_keys = {}

@sio.on('connect')
def connect(sid, environ):
    global count_clients
    count_clients+=1
    print('connect')
    client_updates[sid] = ""

@sio.on('authenticate')
def authenticate(sid, dict):
    global credentials, count_auth_clients
    found = False
    for item in credentials:
        if dict['username'] == item['username']:
            found = True
            if dict['password'] != item['password']:
                sio.disconnect(sid)
            else:
                print('connection authenticated')
                count_auth_clients+=1
                break
    if found == False:
        sio.disconnect(sid)



@sio.on('message')
def message(sid, data):
    print('message ', data)

@sio.on('disconnect')
def disconnect(sid):
    global count_clients
    count_clients-=1
    client_updates.pop(sid)
    print('disconnect', sid)

@sio.on('get_updates')
def get_updates(sid, update):
    global updates_received, client_updates
    updates_received += 1
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

@sio.on('training_status')
def training_status(sid, data):
    global count_train_done
    count_train_done+=1
    print("train status: " + data)
    #secure_agg()

@sio.on('shared_key_status')
def shared_key_status(sid, data):
    global count_shared_done
    count_shared_done+=1
    print("shared status: "+ data)

def connServ():
    eventlet.wsgi.server(eventlet.listen(('', 8004)), app)

'''
def emitServ():
  while True:
    eventlet.greenthread.sleep(seconds=5)
    sio.emit('my message','hello')
'''

def send_model():
    global count_clients, conn_threshold, count_train_done, fin_weights, fin_weights_str, count_auth_clients
    if count_clients >= conn_threshold and count_clients == count_auth_clients:

        print('threshold reached')
        #model_parameters = fl_server.pass_model_parameters()
        #sio.emit('message','server sent you data')
        sio.emit('receive_model', '{"structure" : ' + fin_struct + ', "weights" : ' + fin_weights_str + '}')
        fin_weights = fl_server.weights_from_json(fin_weights_str)
        #secure_agg()
        while count_train_done < count_clients:
            eventlet.greenthread.sleep(seconds=5)
        return True
    return False

def diffie_hellman():
    global pub_keys, count_shared_done
    sio.emit('get_public_keys','send me public keys')
    while len(pub_keys)<count_clients:
        eventlet.greenthread.sleep(seconds=5)
    #print("PUBLIC KEYS RECEIVED")
    #print(pub_keys)
    sio.emit('receive_pub_keys',pub_keys)
    #sio.emit('wait_shared_key',count_clients)
    while count_shared_done < count_clients:
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
    global count_clients, updates_received, update_threshold, client_updates, suv_dictionary, fin_weights, fin_weights_str, count_rounds
    while count_rounds<2:
        print("IN WHILE")
        eventlet.greenthread.sleep(seconds=5)
        if  send_model():
            #secure_agg()
            print("INSIDE SEND MODEL")
            #eventlet.greenthread.sleep(seconds=server_wait_time)
            secure_agg()
            while updates_received < count_clients:
                eventlet.greenthread.sleep(seconds=5)

        #print("PRINTING CLIENT UPDATES:")
        #print(client_updates)
        #for key, value in client_updates.items():
        #    if not value:
        #        sio.emit('message','stop training. new model on the way', room=key)
            sum_updates = fl_server.averaging(client_updates)
            for i in range(0,len(sum_updates)):
                print(fin_weights[i].shape)
                print(sum_updates[i].shape)
                fin_weights[i] = np.add(fin_weights[i],sum_updates[i])

            fin_weights_str = pd.Series(fin_weights).to_json(orient='values')
            sio.emit('clear_round','Clear the round rn')
      #print (client_updates)
            for key, value in client_updates.items():
                client_updates[key] = ""
            updates_received = 0
            suv_dictionary = {}
            count_train_done = 0
            count_shared_done = 0
            count_rounds += 1
            print("-------------------------------------------ROUND COMPLETED-----------------------------------------------------------------------------")

    print("ALL ROUNDS DONE")

    sio.emit('receive_averaged_model','{"structure" : ' + fin_struct + ', "weights" : ' + fin_weights_str + '}')




if __name__ == '__main__':
    pool = eventlet.GreenPool()
    pool.spawn(connServ)
    #pool.spawn(emitServ)
    pool.spawn(federating_process)
    pool.waitall()
