import json
import requests
import os

def collect_attributes(json_data):
    attributes = {}

    def traverse(obj, parent_key=""):
        if isinstance(obj, dict):
            for key, value in obj.items():
                new_key = key
                attributes[new_key] = value
                if isinstance(value, (list, dict)):
                    traverse(value, new_key)
        elif isinstance(obj, list):
            for idx, item in enumerate(obj):
                new_key = f"{parent_key}[{idx}]"
                if isinstance(item, (list, dict)):
                    traverse(item, new_key)
                else:
                    attributes[new_key] = item

    traverse(json_data)
    return attributes

def find_matching_attributes(schema_attr, json_attr, parent_keys=None):
    matching_attributes = {}

    if parent_keys is None:
        parent_keys = []

    for attr, json_value in json_attr.items():
        for schema, schema_value in schema_attr.items():
            if attr.lower() == schema.lower():
                matching_attributes[".".join(parent_keys + [attr])] = json_value
                if isinstance(schema_value, dict):
                    find_matching_attributes(schema_value, json_value, parent_keys + [attr])

    return matching_attributes

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
else:
    print('Failed to download the metadata schema file:', response.text)


# Example JSON data file path
json_data_file = '/home/sarbani/darus_data_harvester/harvester/citation_meta_ex.json'

# Load the JSON data from the file
with open(metadata_schema_file) as f1, open(json_data_file) as f2:
    schema_data = json.load(f1)
    json_data = json.load(f2)

# Collect all attributes
json_attr = collect_attributes(json_data)
schema_attr = collect_attributes(schema_data)

# Find matching attributes and subattributes
matching_attributes = find_matching_attributes(schema_attr, json_attr)

# Save the result to a JSON file
result = {'Citation': matching_attributes}

with open('matching_attributes.json', 'w') as f:
    json.dump(result, f, indent=4)

print(matching_attributes)