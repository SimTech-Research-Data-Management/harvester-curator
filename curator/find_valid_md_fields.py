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

def find_matching_attributes(metadata_schema_file, json_data_file):
    matching_attributes = []

    # Load the JSON data from the file
    with open(metadata_schema_file) as f1, open(json_data_file) as f2:
        schema_data = json.load(f1)
        json_data = json.load(f2)
    
    # Collect all attributes
    json_attr = collect_attributes(json_data)
    schema_attr = collect_attributes(schema_data)


    for attr in json_attr:
        for schema in schema_attr:
            if attr.lower() == schema.lower():
                matching_attributes.append(attr)
                #if isinstance(schema_attr[schema], dict):
                #    subattributes = find_matching_attributes(schema_attr[schema], json_attr[attr])
                #    matching_attributes.extend(subattributes)
                #break
    
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
json_data_file = '/home/sarbani/darus_data_harvester/harvester/harvester_output.json'

# Find matching attributes and subattributes
matching_attributes = find_matching_attributes(metadata_schema_file, json_data_file)

# Save the result to a JSON file
result = {'matching_attributes': matching_attributes}

with open('matching_attributes.json', 'w') as f:
    json.dump(result, f, indent=4)

print(matching_attributes)