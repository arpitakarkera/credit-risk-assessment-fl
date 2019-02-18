import engineio 
import eventlet
import socketio
import time

from flserver import FLServer

sio = socketio.Server(async_mode='eventlet')
app = socketio.Middleware(sio)
count_clients = 0
conn_threshold  = 4
update_threshold = 2
updates_received = 0
client_updates = {}
server_wait_time = 5

fl_server = FLServer()

@sio.on('connect')
def connect(sid, environ):
  global count_clients
  count_clients+=1
  print('connect')
  client_updates[sid] = 0
  #sio.emit('my message', {'data': 'foobar'})

@sio.on('my message')
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
  client_updates[sid] = update


def connServ():
  eventlet.wsgi.server(eventlet.listen(('', 8004)), app)

'''
def emitServ():
  while True: 
    eventlet.greenthread.sleep(seconds=5)
    sio.emit('my message','hello')
'''

def send_model():
  global count_clients, conn_threshold 
  #print('send')
  if count_clients >= conn_threshold :
    #if all(value == None for value in client_updates.values()):
    model_parameters = fl_server.pass_model_parameters()
    sio.emit('receive_model', model_parameters)
    return True 
  return False


def federating_process():
  global count_clients, updates_received, update_threshold, client_updates
  while True:
    eventlet.greenthread.sleep(seconds=5)
    #print('inside f')
    if  send_model():
      eventlet.greenthread.sleep(seconds=server_wait_time)     
      while updates_received < update_threshold:
        eventlet.greenthread.sleep(seconds=5)
        continue
      for key, value in client_updates.items():
        if value is 0:
          sio.emit('my message','stop training. new model on the way', room=key)
      fl_server.averaging(client_updates)
      #print (client_updates)
      for key, value in client_updates.items():
        client_updates[key] = 0
      updates_received = 0

      

        

if __name__ == '__main__':
  pool = eventlet.GreenPool()
  pool.spawn(connServ)
  #pool.spawn(emitServ)
  pool.spawn(federating_process)
  pool.waitall()