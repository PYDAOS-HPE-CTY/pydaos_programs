import os
import time
from pydaos import DCont, DDict
import tset100 as pool_test

# Create a DAOS container
def get_daos_container():
    pool, containers = pool_test.list_containers_in_pool_with_max_targets()
    for container in containers:
        try:
            return pool, container
        except Exception as e:
            print(f"Error accessing container {container}: {e}")
            continue

pool,cont=get_daos_container()
print(pool)
print(cont)
~               
