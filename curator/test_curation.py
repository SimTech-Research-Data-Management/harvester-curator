import json
import os
from pyDaRUS import Dataset
import requests


def get_json_from_api(api_url):
    try:
        response = requests.get(api_url)
        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            # Parse the JSON content
            json_data = response.json()
            return json_data
        else:
            # Print an error message if the request was not successful
            print(f"Error: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None


def get_json_classes(json_data):
    classes = set()

    def extract_classes(data):
        if isinstance(data, dict):
            classes.update(data.keys())
            for value in data.values():
                extract_classes(value)

    extract_classes(json_data)
    return classes


def find_key_recursive(data, target_key):
    if target_key in data:
        return data[target_key]
    for key, value in data.items():
        if isinstance(value, dict):
            result = find_key_recursive(value, target_key)
            if result:
                return result
    return None


def get_compatible_metadatablocks(com_metadata_file, json_data, schema_name, har_json_data, metadata_schema):
    
    # Check if 'metadatablocks' class is present in harvested metadata file
    if 'metadatablocks' not in json_data:
        json_data['metadatablocks'] = {}

    metadatablocks_data = json_data['metadatablocks']

    # Check if 'schema_name' is present under 'metadatablocks'
    if schema_name not in metadatablocks_data:
        # Create 'schema_name' as a subclass
        metadatablocks_data[schema_name] = {}
    
    schema_data = metadatablocks_data[schema_name]

    # Generate metadata for the new 'schema_name'

    # Get the classes from harvested metadata
    har_json_classes = get_json_classes(har_json_data)
    
    # Gets the classes and class_type from metadata schema
    target_key = 'fields'  # Replace with the key you want to search for
    fields = find_key_recursive(metadata_schema, target_key)

    for class_name, class_info in fields.items():
        if class_name in har_json_classes:
            print(class_name)
            har_json_class_data = har_json_data[class_name]
            class_child_fields = class_info.get('childFields')
            title = class_info.get('title')
            class_name = title.replace(' ', '_').lower()
            if class_child_fields:
                schema_data[class_name] = []
                for data in har_json_class_data:
                    schema_data[class_name].append(data)
            else:
                schema_data[class_name] = har_json_class_data
            print(schema_data)

    # Write the updated JSON data back to the file
    with open(com_metadata_file, 'w') as json_file:
        json.dump(json_data, json_file, indent=2)



# File to write compatible metadata
com_metadata_file = "md_com.json"

# Create 'md_com.json' with initial data if it doesn't exist
if os.path.exists(com_metadata_file):
    with open(com_metadata_file, 'w') as file:
        pass

initial_data = {"lib_name": "pyDaRUS"}
with open(com_metadata_file, 'w') as json_file:
    json.dump(initial_data, json_file, indent=2)

with open(com_metadata_file) as json_file:
    com_metadata = json.load(json_file)
    #print(com_metadata)

# Load the harvested JSON file
har_json_file = "test_metadata_example.json"
with open(har_json_file) as file:
    har_json_data = json.load(file)
    #print(har_json_data)

# api endpoints of metadata schemas
api_endpoints_file_path = "md_schema_api_endpoints.json"

try:
    with open(api_endpoints_file_path) as json_file:
        api_blocks = json.load(json_file)

    if not isinstance(api_blocks, list):
        print("Error: JSON file should contain a list of API blocks.")

    for block in api_blocks:
        
        api_url = block.get("api_endpoint")
        schema_name = block.get("name")

        if schema_name and api_url:
            metadata_schema = get_json_from_api(api_url)
            print(f"Processing {schema_name}...\n")
            #search, create and update corresponding matadata
            com_har_metadata = get_compatible_metadatablocks(com_metadata_file, com_metadata, schema_name, har_json_data, metadata_schema)

        else:
            print("Error: Each block should contain a metadata schema 'name' and its 'api_endpoint'.")

except Exception as e:
    print(f"An error occurred while processing API endpoints: {e}")

# A dataset will be created from the harvested information
# Initialize dataset
dataset = Dataset()

# Create a new dataset to which we want to load everything. Here we are using the "from_json" method to initialize the complete dataset
dataset = Dataset.from_json("./md_com.json")

# Check if we recorvered the dataset
print(dataset.yaml())

# Upload the dataset
#p_id = dataset.upload (dataverse_name="roy_dataverse")
#dataset.update(contact_name="Sarbani Roy", contact_email="sarbani.roy@simtech.uni-stuttgart.de")
#print('Dataset created and directory uploaded successfully.')
