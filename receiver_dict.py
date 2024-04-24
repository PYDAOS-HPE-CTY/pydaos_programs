[17:39, 11/04/2024] Vinay MSR: from pydaos import DCont
import pickle

# Initialize DAOS container
daos_cont = DCont("pydaos", "kvstore", None)

daos_dict = None
try:
        daos_dict = daos_cont.get("dict-0")
except DObjNotFound:
        daos_dict = daos_cont.dict("dict-0")

# Define the key under which the object is stored
key = "my_python_object"

# Retrieve the serialized object from the DAOS container
serialized_object = daos_dict.get(key)

# Deserialize the object using pickle
my_object = pickle.loads(serialized_object)

# Now you can use the Python object as needed
print("Name:", my_object["name"])
print("Age:", my_object["age"])
print("City:", my_object["city"])
[17:41, 11/04/2024] Bharat MSR: .
