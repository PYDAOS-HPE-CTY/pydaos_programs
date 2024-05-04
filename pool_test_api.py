import subprocess
import re
from pydaos import DCont, DDict
import json

def convert_to_bytes(size_str, unit):
    # Convert size string to bytes
    size_str = size_str.strip().lower()
    if unit == 'gb':
        return float(size_str) * 1024 * 1024 * 1024
    elif unit == 'mb':
        return float(size_str) * 1024 * 1024
    else:
        return float(size_str)  # Assuming bytes by default

def get_pool_with_max_targets():
    # Run the command and get the output as bytes
    output_bytes = subprocess.check_output(["dmg", "pool", "list"])

    # Decode the bytes to a string
    output_string = output_bytes.decode("utf-8")

    # Split the output into lines and skip the header
    lines = output_string.strip().split("\n")[2:]

    # Initialize variables to keep track of the pool with the highest number of targets
    max_targets = 0
    pool_with_max_targets = ""
    max_free_space_bytes = 0

    # Iterate over each line and extract pool name and number of targets
    for line in lines:
        pool_name = line.split()[0]
        # Run the command to get the number of targets in the pool
        query_output_bytes = subprocess.check_output(["dmg", "pool", "query", pool_name])
        query_output_string = query_output_bytes.decode("utf-8")
        # Extract free space and unit from query output using regex
        free_space_match = re.search(r'Free:\s*([\d..]+)\s*(GB|MB)?', query_output_string)
        if free_space_match:
            free_space_size = free_space_match.group(1)
            unit = free_space_match.group(2)
            free_space_bytes = convert_to_bytes(free_space_size, unit)
        else:
            free_space_bytes = 0

        # Iterate over each line in query output to get target count
        for query_line in query_output_string.split("\n"):
            if 'Target(VOS) count' in query_line:
                # Extract the target count from the line
                num_targets = int(query_line.split(':')[1])

                # If number of targets is greater than the current maximum, update the values
                if num_targets > max_targets:
                    max_targets = num_targets
                    pool_with_max_targets = pool_name
                    max_free_space_bytes = free_space_bytes

                elif num_targets == max_targets:
                    if free_space_bytes > max_free_space_bytes:
                        max_free_space_bytes = free_space_bytes
                        pool_with_max_targets = pool_name

                break  # Stop searching further once the target count is found

    # Return the pool with the highest number of targets
    return pool_with_max_targets

def list_containers_in_pool_with_max_targets():
    # Get the pool with the maximum number of targets
    pool_name = get_pool_with_max_targets()
    
    # Run the command to list containers in the pool with the maximum number of targets
    output_bytes = subprocess.check_output(["daos", "cont", "list", pool_name])

    # Decode the bytes to a string
    output_string = output_bytes.decode("utf-8")

    # Split the output into lines and skip the header
    lines = output_string.strip().split("\n")[2:]

    # Initialize a list to store container names
    containers_in_pool = []

    # Iterate over each line and extract container name
    for line in lines:
        container_name = line.split()[1]
        containers_in_pool.append(container_name)

    # Return the list of container names in the pool with the maximum number of targets
    return pool_name, containers_in_pool


def synchronize_metadata():
    # Initialize a list to store key, pool, container, and chunk size information
    keys_info = []

    # Get a list of pools
    output_bytes = subprocess.check_output(["dmg", "pool", "list"])
    output_string = output_bytes.decode("utf-8")
    lines = output_string.strip().split("\n")[2:]

    # Iterate over each pool
    for line in lines:
        pool_name = line.split()[0]

        # Get a list of containers in the pool
        output_bytes = subprocess.check_output(["daos", "cont", "list", pool_name])
        output_string = output_bytes.decode("utf-8")
        lines = output_string.strip().split("\n")[2:]

        # Iterate over each container in the pool
        for line in lines:
            container_name = line.split()[1]

            daos_cont = DCont(pool_name, container_name, None)

            # Create a DAOS dictionary or get it if it already exists
            try:
                daos_dict = daos_cont.get("pydaos_kvstore_dict")
            except:
                daos_dict = daos_cont.dict("pydaos_kvstore_dict")

            # Get keys information from daos_dict
            unique_keys = set()
            for key in daos_dict:
                # Extract the key prefix
                key_prefix = key.split("chunk")[0]

                # Find the size of the chunk in MB
                chunk_size_mb = 0  # Default chunk size is 0 MB
                if key.endswith("chunk0"):
                    chunk_data = daos_dict[key]
                    chunk_size_bytes = len(chunk_data)  # Get the length of chunk data in bytes
                    # Convert chunk size to MB and round it to the nearest integer
                    chunk_size_mb = round(chunk_size_bytes / (1024 * 1024))

                    unique_keys.add((key_prefix, chunk_size_mb))

            # Append key, pool, container, and chunk size information to the list
            for key_prefix, chunk_size_mb in unique_keys:
                keys_info.append({
                    "key": key_prefix,
                    "chunk_size": chunk_size_mb,
                    "pool": pool_name,
                    "container": container_name
                })

    # Write the list of key, pool, container, and chunk size information to metadata.json
    with open("metadata.json", "w") as json_file:
        json.dump(keys_info, json_file, indent=4)

synchronize_metadata()

