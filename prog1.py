from pydaos import DCont, DDict, DObjNotFound
import json

daos_cont = DCont("pydaos", "kvstore", None) #path to container
daos_dict = None

try:
    daos_dict = daos_cont.get("dict-0")
except DObjNotFound:
    daos_dict = daos_cont.dict("dict-0")

with open('data.json') as json_file:
    data = json.load(json_file)
    for entry in data:
        key = entry["usn"]
        value = entry["name"]
        daos_dict.put(key, value)

while True:
    cmd = input("\nCommand (? for help)> ")
    if cmd == "?":
        print("?\t- Print this help")
        print("r\t- Read a key")
        print("ra\t- Read all keys")
        print("i\t- Insert new key")
        print("d\t- Delete key")
        print("ib\t- Insert new keys in bulk")
        print("rb\t- Read keys in bulk")
        print("q\t- Quit")
    elif cmd == "r":
        key = input("Key? ")
        try:
            print("\tKey:", key, "\tValue:", daos_dict[key])
        except KeyError:
            print("\tError! Key not found")
    elif cmd == "ra":
        print("\nDictionary length =", len(daos_dict))
        for key in daos_dict:
            print("\tKey:", key, "\tValue:", daos_dict[key])
    elif cmd == "i":
        key = input("Enter key: ")
        value = input("Enter value: ")
        daos_dict.put(key, value)
        print("Key-value pair inserted successfully.")
    elif cmd == "d":
        key = input("Key to delete? ")
        if key in daos_dict:
            daos_dict.pop(key)
            print("Key", key, "deleted.")
        else:
            print("Key not found.")
    elif cmd == "ib":
        print("\nInserting new keys in bulk")
        bulk_data = {}
        while True:
            key = input("Enter key (press Enter to finish): ")
            if key == "":
                break
            value = input("Enter value for " + key + ": ")
            bulk_data[key] = value
        daos_dict.bput(bulk_data)
        print("Bulk insertion completed.")
    elif cmd == "rb":
        print("\nReading keys in bulk")
        bulk_keys = []
        while True:
            key = input("Enter key to read (press Enter to finish): ")
            if key == "":
                break
            bulk_keys.append(key)
        result = daos_dict.bget({key: None for key in bulk_keys})
        print("Bulk read result:")
        for key, value in result.items():
            print("\tKey:", key, "\tValue:", value)
    elif cmd == "q":
        break
    else:
        print("Invalid command. Please try again.")
