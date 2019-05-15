import sympy
import random
import numpy as np
from  numpy import array
import pandas as pd
import json
import pickle

from keras.models import Sequential
from keras.layers import Dense
from keras.models import model_from_json
import numpy as np
import pandas as pd
import json
import tensorflow as tf

from privacy.analysis.rdp_accountant import compute_rdp
from privacy.analysis.rdp_accountant import get_privacy_spent
from privacy.dp_query.gaussian_query import GaussianAverageQuery
from privacy.optimizers.dp_optimizer import DPGradientDescentOptimizer

tf.flags.DEFINE_float('noise_multiplier', 1.1, 'Ratio of the standard deviation to the clipping norm')
tf.flags.DEFINE_float('l2_norm_clip', 1.0, 'Clipping norm')
tf.flags.DEFINE_integer('batch_size', 500, 'Batch size')
tf.flags.DEFINE_integer('epochs', 20, 'Number of epochs')
tf.flags.DEFINE_boolean('dpsgd', True, 'If True, train with DP-SGD. If False, ''train with vanilla SGD.')
tf.flags.DEFINE_float('learning_rate', 0.15, 'Learning rate for training')
tf.flags.DEFINE_integer('microbatches', 1, 'Number of microbatches ' '(must evenly divide batch_size)')

FLAGS = tf.flags.FLAGS


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
		dp_average_query = GaussianAverageQuery(FLAGS.l2_norm_clip,FLAGS.l2_norm_clip * FLAGS.noise_multiplier,FLAGS.microbatches)
		optimizer = DPGradientDescentOptimizer(dp_average_query,FLAGS.microbatches,learning_rate=FLAGS.learning_rate,unroll_microbatches=True)
		loss = tf.keras.losses.BinaryCrossentropy(from_logits=True, reduction=tf.losses.Reduction.NONE)
		self.model.compile(loss=loss, optimizer=optimizer, metrics=['accuracy'])
		# self.model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])
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
