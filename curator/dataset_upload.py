import os
import json
import argparse
from easyDataverse import Dataverse

if __name__ == "__main__":
    # Set up argparse for command line arguments
    arg_parser = argparse.ArgumentParser(description="Load metadata from a JSON file.")
    arg_parser.add_argument("--path", help="Path to the compatible metadata JSON file", required=True)
    args = arg_parser.parse_args()
    com_metadata_file = args.path
    
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
    api_token="",
    )

    # Open the JSON file in read mode
    with open(com_metadata_file, 'r') as json_file:
    # Use the loaded JSON data to create a dataset
        dataset = dataverse.dataset_from_json(json_file)

    print(dataset)
