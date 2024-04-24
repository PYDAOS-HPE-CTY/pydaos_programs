# pydaos_programs

# PYDAOS Programs

## Program Descriptions:

### prog2.py
Output:


![image](https://github.com/HPE-MSRIT-CSE-2024/PYDAOS-Programs/assets/164491690/13d70962-d687-47f1-9d10-828d55dbf3d3)


### chunks.py:
- This program uploads a file in chunks of sizes specified by the user and provides the time taken to upload the file in that many number of chunks. 
- It can be used to experiment with different chunk sizes to determine which one takes the least amount of time to upload, as well as to retrieve it from the directory in those many numbers of chunks.
- output
- uploading 200mb file as 10MB chunks
  ![chunk1](https://github.com/HPE-MSRIT-CSE-2024/PYDAOS-Programs/assets/164491690/2c0a638a-d365-4c29-b406-364257fcd6b8)

  uploading 200mb file as 25MB chunks
  ![chunk2](https://github.com/HPE-MSRIT-CSE-2024/PYDAOS-Programs/assets/164491690/81d7925c-3c6b-41d0-8a37-157201d670f7)

  uploading 200mb file as 50MB chunks
  ![chunk3](https://github.com/HPE-MSRIT-CSE-2024/PYDAOS-Programs/assets/164491690/8765ec27-409f-4586-8e1d-869df7a0eb3d)

  



### file_upload.py:
- This program directly uploads a file and provides the time taken to upload. 
- It can be used with files of different sizes to assess how much time each file takes to be uploaded to the DAOS directory.

### sender.py and receiver.py:
- This program stores class definitions in the DAOS directory by serializing them and retrieves them so that an instance of the class, an object, can be created.

- Output screenshot
- 
  ![image](https://github.com/HPE-MSRIT-CSE-2024/PYDAOS-Programs/assets/164491690/5e8dae4f-4be0-4648-a596-2d64b5337699)


### sender_dict.py and receiver_dict.py:
- This program stores dictionary objects in a serialized form in the DAOS directory and retrieves them, allowing their use in a different program.


### test_pool.py
- Returns pool with maximum number of targets and all the containers in that pool
- Can be imported in other programs to automatically find and allocate pools and containers to the program

### auto_chunks.py
- chunks.py with slight modification
- pool and container are not hardcoded, uses test_pool,py to find pool with maximum number of targets


