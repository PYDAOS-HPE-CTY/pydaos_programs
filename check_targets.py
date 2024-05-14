import json
import subprocess
import yaml

def extract_engine_info(yaml_data):
    engine_info = {}
    engine_counter = 1  # Initialize the engine counter
    engines = yaml_data.get('engines', [])
    for engine in engines:
        targets = engine.get('targets', None)
        if targets is not None:
            # Calculate number of CPUs and threads
            nr_xs_helpers = engine.get('nr_xs_helpers', 0)
            first_core = engine.get('first_core', 0)
            num_cpus = 1 + nr_xs_helpers
            num_threads = 2 * num_cpus  # Assuming 2 threads per CPU
            
            engine_info[engine_counter] = {
                'target': targets,
                'num_cpus': num_cpus,
                'num_threads': num_threads
            }
            engine_counter += 1  # Increment the engine counter for the next engine
    return engine_info

def main():
    active_servers = {}
    servers_credentials = {
        "server1": {"ip_address": "127.0.0.1", "username": "vinay", "password": "centos@86"},
        "server2": {"ip_address": "192.168.56.101", "username": "vinay", "password": "centos@86"}
    }

    for server, credentials in servers_credentials.items():
        try:
            ip_address = credentials['ip_address']
            username = credentials['username']
            password = credentials['password']
            # Check if daos_server is running
            ssh_status_command = f'sshpass -p "{password}" ssh -o StrictHostKeyChecking=no {username}@{ip_address} "systemctl is-active daos_server"'
            status_output = subprocess.check_output(ssh_status_command, shell=True)
            status = status_output.decode().strip()
            if status == 'active':
                # Read daos_server.yml
                ssh_command = f'sshpass -p "{password}" ssh -o StrictHostKeyChecking=no {username}@{ip_address} "cat /etc/daos/daos_server.yml"'
                output = subprocess.check_output(ssh_command, shell=True)
                yaml_data_remote = yaml.safe_load(output.decode('utf-8'))
                engine_info_remote = extract_engine_info(yaml_data_remote)
                active_servers[server] = engine_info_remote
        except subprocess.CalledProcessError as e:
            print(f"Error accessing server {server} ({ip_address}): {e.stderr.decode('utf-8')}")

    # Write the active server info to a JSON file
    with open('active_servers_engine_info.json', 'w') as json_file:
        json.dump(active_servers, json_file, indent=4)

if __name__ == "__main__":
    main()
