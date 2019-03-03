from flask import Flask, render_template, request
from flask_cors import CORS
from pymemcache.client import base
from tensorflow.keras.models import model_from_json
import json
import numpy as np
import category_encoders
import pickle
import os
from keras import backend as K
from keras.models import load_model


labelencoderfile = open('encoder/labelencoder', 'rb')
onehotencoderfile = open('encoder/onehotencoder', 'rb')
binaryencoderfile = open('encoder/binaryencoder', 'rb')

binaryencoder = pickle.load(binaryencoderfile)
labelencoder = pickle.load(labelencoderfile)
onehotencoder = pickle.load(onehotencoderfile)

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

def col_transform_onehot (col_name, col_val):
    arr = labelencoder[col_name].transform([col_val])
    arr = arr.reshape(len(arr),1)
    return onehotencoder[col_name].transform(arr)

def col_transform_binary(col_name, col_val):
    x = binaryencoder.transform([col_val])
    return x.loc[0].tolist()

def generate_prediction(input):
      final_input = list()

      #Encoding the inputs
      input_0 = col_transform_onehot('purpose', input[0]).tolist()

      for x in range(len(input_0[0])):
          final_input.append(input_0[0][x])

      for x in input[1:10]:
          final_input.append(x)


      input_10 = col_transform_binary('addr_state', input[10])
      #print("Input 10 is: ")
      #print(input_10)
      for x in input_10:
          final_input.append(x)

      final_input.append(input[11])

      input_12 = col_transform_onehot('home_ownership', input[12]).tolist()
      for x in range(len(input_12[0])):
          final_input.append(x)

      for x in input[13:]:
          final_input.append(x)


      num_arr = np.array(final_input)

      num_arr = np.expand_dims(num_arr, axis = 0)


      print(num_arr.shape)


      model=load_model('models/model.h5')
      pred= model.predict(num_arr)
      print(pred)
      pred = pred[0][0]
      print(pred)
      if pred > 0.5:
          return 'Yes'
      return 'No'

@app.route('/predict', methods=['GET', 'POST'])
def predict():

    K.clear_session()

    input = list()
    input.append(request.form['purpose'])
    input.append(float(request.form['installment']))
    input.append(float(request.form['annual_inc']))
    input.append(float(request.form['dti']))
    input.append(float(request.form['fico']))

    input.append(float(request.form['revol_bal']))
    input.append(float(request.form['revol_util']))
    input.append(float(request.form['inq_last_2m']))
    input.append(float(request.form['delinq_2yrs']))
    input.append(float(request.form['pub_rec']))

    input.append(request.form['addr_state'])
    input.append(int(request.form['emp_length']))
    input.append(request.form['home_ownership'])
    input.append(float(request.form['mths_since_last_delinq']))
    input.append(float(request.form['term']))

    input.append(float(request.form['chargeoff_within_12_mths']))
    input.append(float(request.form['loan_amnt']))
    input.append(float(request.form['open_acc']))
    input.append(float(request.form['total_acc']))

    #print(input)
    #print("\n")

    price=generate_prediction(input)
    return price

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
    if os.path.exists('models/model.h5'):
         os.remove('models/model.h5')
         print('INSIDE')
    model.save('models/model.h5')
    return render_template('predict.html')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8003,debug=True)
