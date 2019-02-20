import sympy
import random
import numpy as np

class FLClient:
	a = 0
	R = 1000
	m = 1
	n = 2
	shared_keys={}
	diffie_parameters={}
	pub_keys = {}
	puvs = {}
	suv = np.zeros(shape=(m,n))
	update = np.zeros(shape=(m,n))
	#bu
	def __init__(self):
		print(" fl_client object made ")

	def generate_public_key(self, diffie_parameters):
		self.a = random.randint(1,100)
		self.diffie_parameters=diffie_parameters
		pub_key = int(pow(self.diffie_parameters["g"],self.a)) % self.diffie_parameters["n"]
		return pub_key

	def generate_shared_key(self):
		for key, value in self.pub_keys.items():
			self.shared_keys[key] = int(pow(value,self.a)) % self.diffie_parameters["n"]
		print("Shared keys")
		print(self.shared_keys)


	def receive_pub_keys(self, pub_keys):
		self.pub_keys = pub_keys
		print ("Pub_keys")
		print(self.pub_keys)
		self.generate_shared_key()

	def encryption(self):
		'''randomly choose value of su,v for each of the other client and encrypt it using
		clients shared key'''
		self.suv = np.random.randint(self.R, size=(self.m,self.n))
		print("suv")
		print(self.suv)
		encrypted_shared_keys = {}
		for key, value in self.shared_keys.items():
			encrypted_shared_keys[key] = self.suv + value
			encrypted_shared_keys[key] = encrypted_shared_keys[key].tolist()
		return encrypted_shared_keys

	def decryption(self,encrypted_suv):
		'''decrypt the sv,u values obtained from other clients'''
		for key, value in encrypted_suv.items():
			encrypted_suv[key] = np.array(encrypted_suv[key])
			#print (type(value))
			#print (type(self.shared_keys[key]))
			encrypted_suv[key] = encrypted_suv[key] - self.shared_keys[key]
		print("encrypted suv")
		print(encrypted_suv)
		for key, value in encrypted_suv.items():
			self.puvs[key] = np.subtract(self.suv, value)
		print("puvs")
		print(self.puvs)



	def train_model(self, model_parameters):
		print("Inside train")
		self.update = np.array([[1,2],[3,4]])
		return True


	def create_update(self):
		'''while updates_received < update_threshold:
			eventlet.greenthread.sleep(seconds=5)
			continue'''
		'''generate pu,v values for all pairs as well as bu and add to the update'''
		#self.train_model(model_parameters)
		sum_puv = np.zeros(shape=(self.m,self.n))
		for key, values in self.puvs.items():
			sum_puv = np.add(sum_puv,values)
		#self.bu= np.random.randint(R, size=(m,n))
		#self.update += sum_puv
		self.update = np.add(self.update,sum_puv)
		#self.update += self.bu
		self.update = self.update.tolist()
		return self.update
