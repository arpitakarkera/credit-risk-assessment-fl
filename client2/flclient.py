import sympy
import random
import numpy as np
from  numpy import array
import pandas as pd
import json
import pickle

DATA_FILE_X = "../data/xtrain.csv"
DATA_FILE_Y = "../data/ytrain.csv"
EPOCHS = 5
BATCH_SIZE = 5000
res_file = "../result/clhistory"

global iter

class FLClient:

	def __init__(self,iter):
		print(" fl_client object made ")
		self.model = None
		self.current_model_version = 0
		# data = np.loadtxt(DATA_FILE, delimiter=",")
		self.iter = iter
		self.X = pd.read_csv(DATA_FILE_X)
		self.Y = pd.read_csv(DATA_FILE_Y)
		self.updates  = []

	def weights_from_json(self,model_weights_json):
		json_load = json.loads(model_weights_json)
		model_weights_list = np.array(json_load)
		model_weights = []
		for i in model_weights_list:
			model_weights.append(np.array(i,dtype=np.float32))
		return model_weights



	def set_model(self, model):
		print( " setting model " )
		self.model = model



	def set_weights(self, model_weights):
		print(" updating model weights ")
		self.model.set_weights(model_weights)

	def train_model(self,model_weights):
		print(" start training ")
		self.model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])
		history  = self.model.fit(self.X, self.Y, epochs=EPOCHS, batch_size=BATCH_SIZE)
		res_file_handler = open(res_file + str(self.iter),"wb")
		print("SAVED AT ITER "+str(self.iter))
		pickle.dump(history, res_file_handler)
		res_file_handler.close()
		#self.updates_json = self.get_updates_json(model_weights)
		self.updates = self.get_updates(model_weights)

		'''for item in self.updates:
			print("ITEM")
			print(item.shape)
			self.dimension.append((item.shape[0],item.shape[1]))'''
		print(" end training ")
		return self.updates

	def get_updates(self, model_weights):
		print(self.model.get_weights())
		# print(model_weights)
		updates =  [(i-j) for (i,j) in zip(self.model.get_weights(),model_weights)]
		# print("PRINTING UPDATES:")
		# print(updates)
		return updates
		#return pd.Series(updates).to_json(orient='values')
