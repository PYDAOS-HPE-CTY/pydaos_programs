import os
import time
from pydaos import DCont, DDict
import pool_test

# Create a DAOS container
def get_daos_container():
    pool, containers = pool_test.list_containers_in_pool_with_max_targets()
    for container in containers:
        try:
            return DCont(pool, container, None)
        except Exception as e:
            print(f"Error accessing container {container}: {e}")
            continue
    

# Create a DAOS container
daos_cont = get_daos_container()

# Create a DAOS dictionary or get it if it already exists
try:
    daos_dict = daos_cont.get("pydaos_kvstore_dict")
except:
    daos_dict = daos_cont.dict("pydaos_kvstore_dict")

# Directory to store uploaded files
upload_dir = "uploads"
os.makedirs(upload_dir, exist_ok=True)

# Size of chunks in MB
n = int(input("Enter size of chunks (in MB): "))
CHUNK_SIZE = n * 1024 * 1024

# Function to print help
def print_help():
    print("?\t- Print this help")
    print("r\t- Read a key")
    print("u\t- Upload file for a new key")
    print("p\t- Display keys")
    print("q\t- Quit")
# Function to read a key with time measurement
def read_key():
    try:
        key = input("Enter key to read: ")
        chunk_count = 0
        assembled_data = b""
        
        start_time = time.time()
        # Fetch all chunks using bget
        chunk_keys = {f"{key}chunk{i}": None for i in range(len(daos_dict))}

        chunks = daos_dict.bget(chunk_keys)
        
        for chunk_key, chunk in chunks.items():
            if chunk is not None:
                assembled_data += chunk
                chunk_count += 1
        
        end_time = time.time()
        retrieval_time = end_time - start_time

        if assembled_data:
            save_value_as_file(key, assembled_data)
            print(f"Value retrieved successfully. Total chunks: {chunk_count}. Time taken: {retrieval_time} seconds")
        else:
            print("Key not found.")

    except Exception as e:
        print(f"Error reading key: {e}")


def save_value_as_file(key, value):
    filename = os.path.join(upload_dir, f"{key}.dat")
    with open(filename, "wb") as f:
        f.write(value)
    print(f"Value saved as file: {filename}")

# Function to print all keys
def print_keys():
    unique_keys = set()
    for key in daos_dict:
        key_prefix = key.split("chunk")[0]
        unique_keys.add(key_prefix)
    for key in unique_keys:
        print(key)


# Function to upload file for a new key with time measurement
def upload_file():
    key = input("Enter new key: ")
    file_path = input("Enter path to file: ")

    if os.path.exists(file_path):
        chunk_dict = {}
        try:
            
            with open(file_path, "rb") as f:
                chunk_count = 0
                while True:
                    data = f.read(CHUNK_SIZE)
                    if not data:
                        break
                    chunk_key = f"{key}chunk{chunk_count}"
                    chunk_dict[chunk_key] = data
                    chunk_count += 1
            # Measure time only for the bput operation
            bput_start_time = time.time()
            daos_dict.bput(chunk_dict)
            bput_end_time = time.time()
            upload_time = bput_end_time - bput_start_time

            print(f"File uploaded in {chunk_count} chunks successfully. Time taken: {upload_time} seconds")
        except Exception as e:
            print(f"Error uploading file: {e}")
    else:
        print("File not found.")

# Main loop
while True:
    print("\nCommands:")
    print_help()
    cmd = input("Enter command (? for help): ")

    if cmd == "?":
        print_help()
    elif cmd == "r":
        read_key()
    elif cmd == "u":
        upload_file()
    elif cmd == "p":
        print_keys()
    elif cmd == "q":
        break
    else:
        print("Invalid command. Enter '?' for help.")

print("Program ended.")
