from flask import Flask, render_template, request
from flask_cors import CORS
from pymemcache.client import base
from tensorflow.keras.models import model_from_json
import json
import numpy as np

mem_client = base.Client(('localhost', 11211))
#mem_client.set('some_key', 'data blah blah blah')
app = Flask(__name__)
CORS(app)

def weights_from_json(model_weights_json):
    json_load = json.loads(model_weights_json)
    model_weights_list = np.array(json_load)
    model_weights = []
    for i in model_weights_list:
        model_weights.append(np.array(i,dtype=np.float32))
    return model_weights

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/getCredentials', methods=['POST'])
def getCredentials():
    username = request.form['username']
    password = request.form['password']
    print(username)
    print(password)
    mem_client.set('username',username)
    mem_client.set('password',password)
    return render_template('message.html')

@app.route('/getConnectionStatus', methods=['POST'])
def getConnectionStatus():
    a = mem_client.get('connection').decode('utf-8')
    return a

@app.route('/getModelStatus', methods=['POST'])
def getModelStatus():
    a = mem_client.get('model_parameters').decode('utf-8')
    return a

@app.route('/getTrainingStatus', methods=['POST'])
def getTrainingStatus():
    a = mem_client.get('training_status').decode('utf-8')
    print(a)
    return a

@app.route('/getUpdateStatus', methods=["POST"])
def getUpdateStatus():
    a = mem_client.get('updates_status').decode('utf-8')
    return a

@app.route('/checkRoundStatus', methods=["POST"])
def checkRoundStatus():
    a = mem_client.get('clear_round_success').decode('utf-8')
    return a


@app.route('/getModel')
def getModel():
    model_string = mem_client.get('model').decode('utf-8')
    print(model_string)
    dict = json.loads(model_string)
    model = model_from_json(json.dumps(dict["structure"]))
    model_weights = weights_from_json(json.dumps(dict["weights"]))
    model.set_weights(model_weights)
    model.save('models/model.h5')
    return render_template('predict.html')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8003,debug=True)
