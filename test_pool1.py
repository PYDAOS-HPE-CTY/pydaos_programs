import subprocess
import re

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
