import numpy as np
import pandas as pd
import json

DATA_FILE = "../data.csv"
EPOCHS = 150
BATCH_SIZE = 10

class FLClient:
    def __init__(self):
        print(" fl_client object made ")
        self.model = None
        self.current_model_version = 0
        data = np.loadtxt(DATA_FILE, delimiter=",")
        self.X = data[:,0:8]
        self.Y = data[:,8]

    def set_model(self, model):
        print( " setting model " )
        self.model = model

    def process_message(self, data):
        print( " processing message " )

    def set_weights(self, model_weights):
        print(" updating model weights ")
        self.model.set_weights(model_weights)

    def train_model(self):
        print(" start training ")
        self.model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])
        self.model.fit(self.X, self.Y, epochs=EPOCHS, batch_size=BATCH_SIZE)
        print(" end training ")

    def get_updates_json(self, model_weights):
        print(self.model.get_weights())
        print(model_weights)
        updates =  [(i-j) for (i,j) in zip(self.model.get_weights(),model_weights)]
        return pd.Series(updates).to_json(orient='values')
