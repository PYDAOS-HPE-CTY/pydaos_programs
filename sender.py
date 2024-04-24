# sender.py

from pydaos import (DCont, DDict, DObjNotFound)

# Define the class
class MyClass:
    def __init__(self, name):
        self.name = name

    def greet(self):
        print("Hello, my name is", self.name)

# Serialize the class definition
class_definition = """
class MyClass:
    def __init__(self, name):
        self.name = name

    def greet(self):
        print("Hello, my name is", self.name)
"""

# Initialize DAOS container
daos_cont = DCont("pydaos", "kvstore", None)

daos_dict = None
try:
        daos_dict = daos_cont.get("dict-0")
except DObjNotFound:
        daos_dict = daos_cont.dict("dict-0")

# Store the class definition in the PyDAOS container
daos_dict.put("my_class_definition", class_definition)
