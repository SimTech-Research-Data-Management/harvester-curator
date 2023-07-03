import json
import requests
import os

def collect_attributes(json_data):
    attributes = set()

    def traverse(obj):
        if isinstance(obj, dict):
            for key, value in obj.items():
                attributes.add(key)
                traverse(value)
        elif isinstance(obj, (list, tuple)):
            for item in obj:
                traverse(item)

    traverse(json_data)
    return attributes

def is_metadata_field(attribute, metadata_fields):
    return attribute.lower() in metadata_fields

# URL of the metadata schema file in the GitHub repository
metadata_schema_url = 'https://raw.githubusercontent.com/JR-1991/pyDaRUS/main/pyDaRUS/templates/json/Citation.json'

# Download the metadata schema file from the GitHub repository
response = requests.get(metadata_schema_url)
if response.status_code == 200:
    # Specify the local path to save the metadata schema file
    metadata_schema_file = './DaRUS/Citation/Citation.json'

    # Create the directory structure if it doesn't exist
    os.makedirs(os.path.dirname(metadata_schema_file), exist_ok=True)


    # Save the file locally
    with open(metadata_schema_file, 'w') as f:
        f.write(response.text)

    # Load the metadata schema from the file
    with open(metadata_schema_file) as f:
        schema = json.load(f)
        metadata_fields = schema['Citation'].keys()

    # Load the metadata schema from the file
    with open(metadata_schema_file) as f:
        schema = json.load(f)
        metadata_fields = schema['Citation'].keys()

    # Example JSON data file path
    json_data_file = '/home/sarbani/darus_data_harvester/harvester/harvester_output.json'

    # Load the JSON data from the file
    with open(json_data_file) as f:
        json_data = json.load(f)

    # Collect all attributes from the JSON data
    json_attributes = collect_attributes(json_data)

    # Check if each attribute is a valid metadata field
    # Group valid and not-valid metadata fields
    valid_fields = []
    invalid_fields = []
    for attribute in json_attributes:
        if is_metadata_field(attribute, metadata_fields):
            valid_fields.append(attribute)
        else:
            invalid_fields.append(attribute)

    # Print the results
    print("Valid metadata fields:")
    for field in valid_fields:
        print(field)
    
    print("\nNot a valid metadata fields:")
    for field in invalid_fields:
        print(field)
else:
    print('Failed to download the metadata schema file:', response.text)
