import os
import json
import time
from pydaos import DCont, DDict
import pool_test_api as pool_test
import re


POOL_METADATA_FILE="pool_metadata.json"
# Create a DAOS container
def get_daos_container():
  pool, containers = pool_test.list_containers_in_pool_with_max_targets()
  containers.sort()

  try:
    with open(POOL_METADATA_FILE, "r") as f:
      metadata = json.load(f)
  except (FileNotFoundError, json.JSONDecodeError):
    metadata = {}
    pass  

  pool_data = metadata.get(pool, {})
  if not pool_data:
    pool_data = {"containers": containers.copy(), "last_used_index": -1}  
    metadata[pool] = pool_data

  last_used_index = pool_data["last_used_index"]

  last_used_index = metadata.get(pool, {}).get("last_used_index", -1) % len(containers)
  metadata[pool] = {"containers": containers.copy(), "last_used_index": (last_used_index + 1) % len(containers)}


  with open(POOL_METADATA_FILE, "w") as f:
    json.dump(metadata, f, indent=4)

  selected_container = containers[last_used_index]
  return pool,selected_container

        
    
# Directory to store uploaded files
upload_dir = "uploads"
os.makedirs(upload_dir, exist_ok=True)

# Metadata file path
metadata_file = "metadata.json"

# Size of chunks in MB
pool_test.synchronize_metadata()
# Function to print help
def print_help():
    print("?\t- Print this help")
    print("r\t- Read a key")
    print("u\t- Upload file for a new key")
    print("p\t- Display keys")
    print("d\t- Delete a key")
    print("q\t- Quit")

# Function to read a key with time measurement
def read_key():

   
    try:
        key = input("Enter key to read: ")
        
        # Search for key in metadata JSON file
        pool, cont = get_pool_and_container_from_metadata(key)
        
        if pool is None or cont is None:
            print("Key not found in metadata.")
            return

        daos_cont = DCont(pool, cont, None)

        # Create a DAOS dictionary or get it if it already exists
        try:
            daos_dict = daos_cont.get("pydaos_kvstore_dict")
        except:
            daos_dict = daos_cont.dict("pydaos_kvstore_dict")

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

# Function to get pool and container names from metadata
def get_pool_and_container_from_metadata(key):
    try:
        with open(metadata_file, "r") as f:
            metadata = json.load(f)
            for entry in metadata:
                if entry["key"] == key:
                    return entry["pool"], entry["container"]
    except Exception as e:
        print(f"Error retrieving metadata: {e}")
    return None, None

def save_value_as_file(key, value):
    filename = os.path.join(upload_dir, f"{key}.dat")
    with open(filename, "wb") as f:
        f.write(value)
    print(f"Value saved as file: {filename}")

# Function to print all keys, pools, and containers in three columns
def print_keys():
    pool_test.synchronize_metadata()
    try:
        with open(metadata_file, "r") as f:
            metadata = json.load(f)
            print("{:<30} {:<30} {:<30} {:<30}".format("Key","chunk size", "Pool", "Container"))
            print("-" * 90)
            for entry in metadata:
                print("{:<30} {:<30} {:<30} {:<30}".format(entry['key'],entry['chunk_size'],entry['pool'], entry['container']))
    except Exception as e:
        print(f"Error retrieving metadata: {e}")


# Function to upload file for a new key with time measurement
def upload_file():
    key = input("Enter new key: ")
    file_path = input("Enter path to file: ")

    n = int(input("Enter size of chunks (in MB): "))
    CHUNK_SIZE = n * 1024 * 1024

    try:
        pool,cont = get_daos_container()
        
        daos_cont=DCont(pool, cont, None)

        # Create a DAOS dictionary or get it if it already exists
        try:
            daos_dict = daos_cont.get("pydaos_kvstore_dict")
        except:
            daos_dict = daos_cont.dict("pydaos_kvstore_dict")
        
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
                
                # Store metadata
                metadata = {
                    "key": key,
                    "pool": pool,
                    "container": cont
                }
                #store_metadata(metadata)
                pool_test.synchronize_metadata()

                print(f"File uploaded in Pool:{pool}, Container:{cont}, {chunk_count} chunks successfully. Time taken: {upload_time} seconds")
            except Exception as e:
                print(f"Error uploading file: {e}")
        else:
            print("File not found.")
    except Exception as e:
        print(f"Error accessing container: {e}")

# Function to store metadata
def store_metadata(metadata):
    if not os.path.exists(metadata_file):
        with open(metadata_file, "w") as f:
            json.dump([], f)
    with open(metadata_file, "r+") as f:
        data = json.load(f)
        data.append(metadata)
        f.seek(0)
        json.dump(data, f, indent=4)

def delete_key(key):
    try:
        # Get the pool and container from metadata
        pool, container = None, None
        with open(metadata_file, "r") as f:
            metadata = json.load(f)
            for entry in metadata:
                if entry['key'] == key:
                    pool = entry['pool']
                    container = entry['container']
                    break
        
        if pool is None or container is None:
            print("Key not found in metadata.")
            return
        
        # Connect to the DAOS container
        daos_cont = DCont(pool, container, None)
        
        # Retrieve the DAOS dictionary
        try:
            daos_dict = daos_cont.get("pydaos_kvstore_dict")
        except:
            daos_dict = daos_cont.dict("pydaos_kvstore_dict")
        
        # Delete all keys with the given key prefix
        chunk_keys = {f"{key}chunk{i}": None for i in range(len(daos_dict))}
        if chunk_keys:
            for chunk_key in chunk_keys:
                daos_dict.pop(chunk_key)
            print(f"Key'{key}' removed from the container.")
        else:
            print(f"No keys found matching '{key}' in the container.")
        
        pool_test.synchronize_metadata()
            
    except Exception as e:
        print(f"Error deleting key: {e}")


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
    elif cmd == "d":
        key_to_delete = input("Enter the key to delete: ")
        delete_key(key_to_delete)
    elif cmd == "q":
        break
    else:
        print("Invalid command. Enter '?' for help.")

print("Program ended.")
