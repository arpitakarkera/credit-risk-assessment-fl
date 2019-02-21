import sympy
import random
import numpy as np
from  numpy import array
import hashlib
import pyaes
import pyDHE

class FLClient:
	a = 0
	R = 1000
	m = 2
	n = 2
	shared_keys={}
	diffie_parameters={}
	pub_keys = {}
	puvs = {}
	suv = np.zeros(shape=(m,n))
	update = np.zeros(shape=(m,n))
	Alice = None
	#bu
	def __init__(self):
		print(" fl_client object made ")

	def generate_public_key(self, diffie_parameters):
		self.a = random.randint(1,100)
		self.diffie_parameters=diffie_parameters
		pub_key = int(pow(self.diffie_parameters["g"],self.a)) % self.diffie_parameters["n"]
		return pub_key

	def generate_shared_key(self):
		#print("PUBLIC KEYS SIZE:")
		#print(len(self.pub_keys))
		for key, value in self.pub_keys.items():
			self.shared_keys[key] = self.Alice.update(value)
		#print("SHARED KEYS")
		#print(len(self.shared_keys))


	def receive_pub_keys(self, pub_keys, Alice):
		self.pub_keys = pub_keys
		self.Alice = Alice
		self.generate_shared_key()

	def encryption(self):
		'''randomly choose value of su,v for each of the other client and encrypt it using
		clients shared key'''
		self.suv = np.random.randint(self.R, size=(self.m,self.n))
		print("suv")
		print(self.suv)
		encrypted_suvs = {}
		#print("SHARED KEYS SIZE:")
		#print(len(self.shared_keys))
		for key, value in self.shared_keys.items():
			value = str(value).encode('utf-8')
			key_maker = hashlib.md5(value)
			key_32 = key_maker.hexdigest().encode('utf-8')
			aes = pyaes.AESModeOfOperationCTR(key_32)
			plain_text = repr(self.suv)
			cipher_text = aes.encrypt(plain_text)
			encrypted_suvs[key] = cipher_text
		return encrypted_suvs


	def decryption(self,encrypted_suv):
		'''decrypt the sv,u values obtained from other clients'''
		for key, value in encrypted_suv.items():
			shared_key = str(self.shared_keys[key])
			key_maker = hashlib.md5(shared_key.encode('utf-8'))
			key_32 = key_maker.hexdigest().encode('utf-8')
			aes = pyaes.AESModeOfOperationCTR(key_32)
			decrypted = aes.decrypt(encrypted_suv[key])
			encrypted_suv_str = decrypted.decode(encoding='utf-8', errors='replace')
			encrypted_suv_np = eval(encrypted_suv_str)
			encrypted_suv[key] = encrypted_suv_np
			#print (type(value))
			#print (type(self.shared_keys[key]))
		#print("DECRYPTED SUVS NOW:")
		#print(encrypted_suv)
		for key, value in encrypted_suv.items():
			self.puvs[key] = np.subtract(self.suv, value)
		#print("puvs")
		#print(self.puvs)



	def train_model(self, model_parameters):
		print("Inside train")
		self.update = np.array([[1,2],[3,4]])
		return True

	def deleteVal(self):
		self.shared_keys = {}
		self.diffie_parameters = {}
		self.pub_keys = {}
		self.puvs = {}
		self.suv = np.zeros(shape=(self.m,self.n))
		self.update = np.zeros(shape=(self.m,self.n))


	def create_update(self):
		'''while updates_received < update_threshold:
			eventlet.greenthread.sleep(seconds=5)
			continue'''
		'''generate pu,v values for all pairs as well as bu and add to the update'''
		#self.train_model(model_parameters)
		sum_puv = np.zeros(shape=(self.m,self.n))
		#print("INITIAL SUM VEC:")
		#print(sum_puv)
		#print("PRINTING PUVS AGAIN:")
		#print(self.puvs)
		for key, values in self.puvs.items():
			sum_puv = np.add(sum_puv,values)
		#self.bu= np.random.randint(R, size=(m,n))
		#self.update += sum_puv
		self.update = np.add(self.update,sum_puv)
		#self.update += self.bu
		print("update")
		print(self.update)
		self.update = self.update.tolist()
		#print("LIST UPDATE:")
		#print(self.update)
		return self.update
