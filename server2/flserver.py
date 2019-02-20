import sympy
import numpy as np

class FLServer:
	encrypted_suvs = {}
	def __init__(self):
		print("fl_server object made")

	def pass_model_parameters(self):
		parameters = "parameters"
		return parameters

	def averaging(self, updates):
		for key, value in updates.items():
			shp = value.shape
			break
		sum_updates = np.zeros(shp)
		for key, value in updates.items():
			sum_updates = np.add(sum_updates, value)
		print(sum_updates)



	def diffie_parameters(self):
		g = sympy.randprime(1,100)
		n = sympy.randprime(10000,100000)
		return {"g":g,"n":n}

	def perturb_util1(self, dict):
		for key, value in dict.items():
			self.encrypted_suvs[key] = {}
		for key, value in dict.items():
			for key_in, value_in in value.items():
				if(key != key_in):
					self.encrypted_suvs[key_in][key] = value_in
		return self.encrypted_suvs
