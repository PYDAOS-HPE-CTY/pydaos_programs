#receiver.py

from pydaos import DCont, DObjNotFound

# Initialize DAOS container
daos_cont = DCont("pydaos", "kvstore", None)

daos_dict = None
try:
        daos_dict = daos_cont.get("dict-0")
except DObjNotFound:
        daos_dict = daos_cont.dict("dict-0")

# Retrieve the class definition from the PyDAOS container
try:
    class_definition = daos_dict.get("my_class_definition").decode("utf-8")
    exec(class_definition)
except DObjNotFound:
    print("Class definition not found in PyDAOS.")

# Check if the class definition was successfully retrieved
try:
    MyClass  # Check if MyClass is defined
except NameError:
    print("Failed to retrieve the class definition. Check the class definition.")

# Create an instance of the retrieved class
try:
    my_instance = MyClass("Alice")
    my_instance.greet()  # Output: Hello, my name is Alice
except NameError:
    print("Failed to create an instance. Class definition may be missing or incorrect.")
