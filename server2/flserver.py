import sympy
import numpy as np

class FLServer:
	encrypted_suvs_clientwise = {}
	def __init__(self):
		print("fl_server object made")

	def pass_model_parameters(self):
		parameters = "parameters"
		return parameters

	def deleteVal(self):
		self.encrypted_suvs_clientwise = {}

	def averaging(self, updates):
		for key, value in updates.items():
			shp = value.shape
			break
		sum_updates = np.zeros(shp)
		for key, value in updates.items():
			sum_updates = np.add(sum_updates, value)
		print("PRINTING SUM UPDATES:")
		print(sum_updates)
		#print("ENCRYPTED SUVS CLIENTWISE")
		#print(self.encrypted_suvs_clientwise)
		self.deleteVal()



	def diffie_parameters(self):
		g = sympy.randprime(1,100)
		n = sympy.randprime(10000,100000)
		return {"g":g,"n":n}

	def perturb_util1(self, dict):
		#print("DICTIONARY PRINTING:")
		#print(dict)
		for key, value in dict.items():
			self.encrypted_suvs_clientwise[key] = {}
		for key, value in dict.items():
			for key_in, value_in in value.items():
				if(key != key_in):
					self.encrypted_suvs_clientwise[key_in][key] = value_in
		#print("ENCRYPTED SUVS CLIENTWISE:")
		#print(self.encrypted_suvs_clientwise)
		return self.encrypted_suvs_clientwise
