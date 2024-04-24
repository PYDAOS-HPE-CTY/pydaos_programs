import os
import json
from pydaos import DCont, DDict

# Create a DAOS container
daos_cont = DCont("pydaos", "kvstore", None)

# Create a DAOS dictionary or get it if it already exists
try:
    daos_dict = daos_cont.get("pydaos_kvstore_dict")
except:
    daos_dict = daos_cont.dict("pydaos_kvstore_dict")

# Directory to store uploaded files
upload_dir = "uploads"
os.makedirs(upload_dir, exist_ok=True)

# Function to print help
def print_help():
    print("?\t- Print this help")
    print("r\t- Read a key")
    print("u\t- Upload file for a new key")
    print("ub\t- Upload files for new keys in bulk")
    print("d\t- Delete key")
    print("p\t- Display keys")
    print("q\t- Quit")


# Function to read a key
def read_key():
    try:
        key = input("Enter key to read: ")
        value = daos_dict[key]
        if value:
                save_value_as_file(key, value)
        else:
                print("Key not found.")

    except KeyError:
        print("\tError! Key not found")

# Function to save value as a file
def save_value_as_file(key, value):
    filename = os.path.join(upload_dir, f"{key}.dat")
    with open(filename, "wb") as f:
        f.write(value)
    print(f"Value saved as file: {filename}")

#Function to print all keys
def print_keys():
    for i in daos_dict:
        print(i)

# Function to upload file for a new key
def upload_file():
    key = input("Enter new key: ")
    if key not in daos_dict:
         file_path = input("Enter path to file: ")
         if os.path.exists(file_path):
                 with open(file_path, "rb") as f:
                         value = f.read()
                 daos_dict.put(key, value)
                 print("File uploaded successfully.")
         else:
                 print("File not found.")
    else:
         print("Key already exists")

# Function to delete a key
def delete_key():
    key = input("Enter key to delete: ")
    if daos_dict.pop(key) is None:
        print("Key deleted successfully.")
    else:
        print("Key not found.")

# Function to upload files for new keys in bulk
def upload_bulk():
    num_keys = int(input("Enter the number of keys to insert: "))
    for i in range(num_keys):
        key = input(f"Enter key {i + 1}: ")
        file_path = input(f"Enter path to file for key {key}: ")
        if os.path.exists(file_path):
            with open(file_path, "rb") as f:
                value = f.read()
            daos_dict.put(key, value)
            print(f"File uploaded for key {key} successfully.")
        else:
            print(f"File not found for key {key}.")

# Main loop
print_help()

while True:
    print("\nCommands:")
    cmd = input("Enter command (? for help): ")

    if cmd == "?":
        print_help()
    elif cmd == "r":
        read_key()
    elif cmd == "u":
        upload_file()
    elif cmd == "d":
        delete_key()
    elif cmd == "ub":
        upload_bulk()
    elif cmd=='p':
        print_keys()
    elif cmd == "q":
        break
    else:
        print("Invalid command. Enter '?' for help.")

print("Program ended.")
