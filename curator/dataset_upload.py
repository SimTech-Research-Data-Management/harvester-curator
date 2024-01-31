# from easyDataverse import Dataverse

# dataverse = Dataverse(
#   server_url="https://darus.uni-stuttgart.de",
#   api_token="3be89818-d34c-422d-a3fb-136d5cd253dc",
# )

# json_file_path = "/Users/sarbani/Simtech_works/Harvester-Curator/example/md_com.json"

# # Open the JSON file in read mode
# with open(json_file_path, 'r') as json_file:
#     dataset = dataverse.dataset_from_json(json_file)

# print(dataset)

import os
import json
from easyDataverse import Dataverse

# Your JSON file path
com_metadata_file = "/Users/sarbani/Simtech_works/Harvester-Curator/example/md_com.json"

# Check if 'md_com.json' exists and has content
if os.path.exists(com_metadata_file) and os.path.getsize(com_metadata_file) > 0:
    # Open the JSON file for reading
    with open(com_metadata_file, 'r') as json_file:
        # Load the JSON data into a Python dictionary
        com_metadata = json.load(json_file)
else:
    # If the file doesn't exist or is empty, initialize an empty dictionary
    com_metadata = {}

# Initialize Dataverse instance
dataverse = Dataverse(
    server_url="https://darus.uni-stuttgart.de",
    api_token="3be89818-d34c-422d-a3fb-136d5cd253dc",
)

# Open the JSON file in read mode
with open(com_metadata_file, 'r') as json_file:
    # Use the loaded JSON data to create a dataset
    dataset = dataverse.dataset_from_json(json_file)

print(dataset)
