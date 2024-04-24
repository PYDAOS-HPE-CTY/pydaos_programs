from pydaos import DCont, DObjNotFound
import pickle

# Initialize DAOS container
daos_cont = DCont("pydaos", "kvstore", None)

daos_dict = None
try:
        daos_dict = daos_cont.get("dict-0")
except DObjNotFound:
        daos_dict = daos_cont.dict("dict-0")


# Define a key for the object
key = "my_python_object"

# Define the Python object to be saved
my_object = {
    "name": "John",
    "age": 30,
    "city": "New York"
}

# Serialize the object using pickle
serialized_object = pickle.dumps(my_object)

# Store the serialized object in the DAOS container
try:
    # If the object already exists, delete it first
    daos_dict.pop(key)
except DObjNotFound:
    pass

# Store the serialized object
daos_dict.put(key, serialized_object)

print("Python object saved successfully.")
