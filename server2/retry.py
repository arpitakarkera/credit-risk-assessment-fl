# from keras.models import Sequential
# from keras.layers import Dense
# from keras.models import model_from_json
# import numpy as np
# import pandas as pd
# import json
# import tensorflow as tf
#
# from privacy.analysis.rdp_accountant import compute_rdp
# from privacy.analysis.rdp_accountant import get_privacy_spent
# from privacy.dp_query.gaussian_query import GaussianAverageQuery
# from privacy.optimizers.dp_optimizer import DPGradientDescentOptimizer
#
# tf.flags.DEFINE_float('noise_multiplier', 1.1, 'Ratio of the standard deviation to the clipping norm')
# tf.flags.DEFINE_float('l2_norm_clip', 1.0, 'Clipping norm')
# tf.flags.DEFINE_integer('batch_size', 500, 'Batch size')
# tf.flags.DEFINE_integer('epochs', 20, 'Number of epochs')
# tf.flags.DEFINE_boolean('dpsgd', True, 'If True, train with DP-SGD. If False, ''train with vanilla SGD.')
# tf.flags.DEFINE_float('learning_rate', 0.15, 'Learning rate for training')
# tf.flags.DEFINE_integer('microbatches', 1, 'Number of microbatches ' '(must evenly divide batch_size)')
#
# FLAGS = tf.flags.FLAGS
#
#
# EPOCHS = 1000
# BATCH_SIZE = 5000
# X = pd.read_csv("../data/x10k.csv")
# Y = pd.read_csv("../data/y10k.csv")
# test_data = pd.read_csv("../data/x1k.csv")
# test_labels = pd.read_csv("../data/y1k.csv")
#
# dp_average_query = GaussianAverageQuery(FLAGS.l2_norm_clip,FLAGS.l2_norm_clip * FLAGS.noise_multiplier,FLAGS.microbatches)
# optimizer = DPGradientDescentOptimizer(dp_average_query,FLAGS.microbatches,learning_rate=FLAGS.learning_rate,unroll_microbatches=True)
# loss = tf.keras.losses.BinaryCrossentropy(from_logits=True, reduction=tf.losses.Reduction.NONE)
#
# model = Sequential()
# model.add(Dense(20, input_dim=43, activation="relu", kernel_initializer="uniform"))
# model.add(Dense(10, activation="relu", kernel_initializer="uniform"))
# model.add(Dense(1, activation="sigmoid", kernel_initializer="uniform"))
#
# model.compile(loss=loss, optimizer=optimizer, metrics=['accuracy'])

from keras.models import Sequential
from keras.layers import Dense
from keras.models import model_from_json
import numpy as np
import pandas as pd
import json


test_data = pd.read_csv("../data/x1k.csv")
test_labels = pd.read_csv("../data/y1k.csv")

model = Sequential()
model.add(Dense(20, input_dim=43, activation="relu", kernel_initializer="uniform"))
model.add(Dense(10, activation="relu", kernel_initializer="uniform"))
model.add(Dense(1, activation="sigmoid", kernel_initializer="uniform"))

model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])



# serialize model to JSON
model_json = model.to_json()
model_weights = model.get_weights()
# print()
model_weights_json = pd.Series(model_weights).to_json(orient='values')
# print(type(model_weights))
# print(type(model_weights[0]))
# for i in model_weights:
#     print(type(i))
# print(type(model_weights))
# model.set_weights(model_weights)
# print(model.summary())
# def weights_from_json(model_weights_json):
# 	json_load = json.loads(model_weights_json)
# 	model_weights_list = np.array(json_load)
# 	model_weights = []
# 	for i in model_weights_list:
# 		model_weights.append(np.array(i,dtype=np.float32))
# 	return model_weights
# ########################
# model_weights_json = pd.Series(model_weights).to_json(orient='values')
# mw2 = weights_from_json(model_weights_json)
# m2 = model_from_json(model_json)
# m2.set_weights(mw2)
# def weights_from_json(model_weights_json):
# 	json_load = json.loads(model_weights_json)
# 	model_weights_list = np.array(json_load)
# 	model_weights = []
# 	for i in model_weights_list:
# 		model_weights.append(np.array(i,dtype=np.float32))
# 	return model_weights
#
# print(model== m2)
# print(np.array_equal(model_weights,mw2))
# c = 0
# for (i,j) in zip(model_weights,mw2):
#     print(i.shape)
#     print(j.shape)
#     print()
#     print(c)
#     if c == 0 or c == 2:
#         print(type(i[0]))
#         print(type(j[0]))
#         for (m,n) in zip(i,j):
#             if not (np.array_equal(m,n)):
#                 for (p,q) in zip(m,n):
#                     print(p,q)
#                 # print(type(m))
#                 # print(type(n))
#     c += 1

# with open("model.json", "w") as json_file:
#     json_file.write(model_json)
# # serialize weights to HDF5
# model.save_weights("model.h5")
# print("Saved model to disk")
#
#
# json_file = open('model.json', 'r')
# loaded_model_json = json_file.read()
# json_file.close()
# loaded_model = model_from_json(loaded_model_json)
# # load weights into new model
# loaded_model.load_weights("model.h5")
# print("Loaded model from disk")
