import numpy as np
from numpy import array
import hashlib
import pyaes
import pyDHE
import pandas as pd

class SecureAggregation:
    """docstring for SecureAggregation."""
    R = 1000
    shared_keys={}
    diffie_parameters={}
    pub_keys = {}
    puvs = {}
    suv = []
    updates  = []
    Alice = None

    def __init__(self):
        print("Secure aggregation object made")

    def get_shared_key_length(self):
        return len(self.shared_keys)

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
        return True
		#print("SHARED KEYS")
		#print(len(self.shared_keys))


    def receive_pub_keys(self, pub_keys, Alice):
        self.pub_keys = pub_keys
        self.Alice = Alice
        self.generate_shared_key()

    def encryption(self, updates):
        self.updates = updates
        for item in self.updates:
            self.suv.append(np.random.randint(self.R, size=item.shape))
        print("suv")
        print(self.suv)
        encrypted_suvs = {}
        print("SHARED KEYS SIZE:")
        print(len(self.shared_keys))
        for key, value in self.shared_keys.items():
            value = str(value).encode('utf-8')
            key_maker = hashlib.md5(value)
            key_32 = key_maker.hexdigest().encode('utf-8')
            aes = pyaes.AESModeOfOperationCTR(key_32)

            cipher_text = []
            for item in self.suv:
                plain_text = repr(item)
                cipher_text.append(aes.encrypt(plain_text))

            encrypted_suvs[key] = cipher_text
            print(len(self.shared_keys))
        return encrypted_suvs


    def decryption(self,encrypted_suv):
        decrypted_suv = {}
        for key, value in encrypted_suv.items():
            shared_key = str(self.shared_keys[key])
            key_maker = hashlib.md5(shared_key.encode('utf-8'))
            key_32 = key_maker.hexdigest().encode('utf-8')
            aes = pyaes.AESModeOfOperationCTR(key_32)

            decrypted_suv_list=[]
            for item in value:
                decrypted = aes.decrypt(item)
                decrypted_suv_str = decrypted.decode(encoding='utf-8', errors='replace')
                decrypted_suv_list.append(eval(decrypted_suv_str))
            decrypted_suv[key] = decrypted_suv_list
			#print (type(value))
			#print (type(self.shared_keys[key]))
		#print("DECRYPTED SUVS NOW:")
		#print(encrypted_suv)
        for key, value in decrypted_suv.items():
            puv_list = []
            for i in range(0, len(value)):
                puv_list.append(np.subtract(self.suv[i],value[i]))
            self.puvs[key] = puv_list
		#print("puvs")
		#print(self.puvs)

    def deleteVal(self):
        self.shared_keys = {}
        self.diffie_parameters = {}
        self.pub_keys = {}
        self.puvs = {}
        self.suv = []
        self.updates = []
        self.dimension = []


    def create_update(self):
        sum_puv = []
        for key, value in self.puvs.items():
            for item in value:
                sum_puv.append(np.zeros_like(item))
            break
		#np.zeros(shape=(self.m,self.n))
		#print("INITIAL SUM VEC:")
		#print(sum_puv)
		#print("PRINTING PUVS AGAIN:")
		#print(self.puvs)
        for key, value in self.puvs.items():
            for i in range(0, len(value)):
                sum_puv[i] = np.add(sum_puv[i], value[i])

		#self.bu= np.random.randint(R, size=(m,n))
		#self.update += sum_puv
        for i in range(0, len(self.updates)):
            self.updates[i] = np.add(self.updates[i],sum_puv[i])
		#self.update += self.bu
        print("update")
        print(self.updates)
        updates = pd.Series(self.updates).to_json(orient='values')
		#print("LIST UPDATE:")
		#print(self.update)
        return updates
