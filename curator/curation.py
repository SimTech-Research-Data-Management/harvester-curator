import json
import os
from pyDaRUS import Dataset, Privacy

def get_json_classes(json_data):
    classes = set()

    def extract_classes(data):
        if isinstance(data, dict):
            classes.update(data.keys())
            for value in data.values():
                extract_classes(value)

    extract_classes(json_data)
    return classes


def get_compatible_metadatablocks(com_metadata_file, json_data, schema_name, har_json_data, metadata_schema):
    # Check if 'metadatablocks' class is present
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
    properties = metadata_schema.get('properties', {})
    classes_info = {}

    for class_name, class_info in properties.items():
        class_type_class = class_info.get('typeClass')
        classes_info[class_name] = {'type_class': class_type_class}

    # Matching the the classes from harvested metadata with schema classes and poulate the json file with corresponding data
    for class_name, class_info in classes_info.items():
        if class_name in har_json_classes:
            har_json_class_data = har_json_data[class_name]
            if class_info['type_class'] == "compound":
                schema_data[class_name] = []
                for data in har_json_class_data:
                    schema_data[class_name].append(data)
            else:
                schema_data[class_name] = har_json_class_data

    # Write the updated JSON data back to the file
    with open(com_metadata_file, 'w') as json_file:
        json.dump(json_data, json_file, indent=2)


# File to write compatible metadata
com_metadata_file = "md_com.json"

# Create 'md_com.json' with initial data if it doesn't exist
if not os.path.exists(com_metadata_file):
    initial_data = {"lib_name": "pyDaRUS"}
    with open(com_metadata_file, 'w') as json_file:
        json.dump(initial_data, json_file, indent=2)

with open(com_metadata_file) as json_file:
    com_metadata = json.load(json_file)

# Load the harvested JSON file
har_json_file = "harvested_metadata_example.json"
with open(har_json_file) as file:
    har_json_data = json.load(file)

# Folder containing metadata schema files
schema_folder = "./metadata_schema_DaRUS"

# Load metadata schema files programmatically
metadata_schemas = {}

for filename in os.listdir(schema_folder):
    if filename.endswith(".json"):
        schema_file_path = os.path.join(schema_folder, filename)
        schema_name = os.path.splitext(filename)[0]

        with open(schema_file_path) as schema_file:
            metadata_schemas[schema_name] = json.load(schema_file)

# Process for each loaded schema
for schema_name, metadata_schema in metadata_schemas.items():
    
    print(f"Processing {schema_name} metadata")

    #search if corresponding metadata class already exixts
    com_har_metadata = get_compatible_metadatablocks(com_metadata_file, com_metadata, schema_name, har_json_data, metadata_schema)

# A dataset will be created from the harvested information
# Initialize dataset
dataset = Dataset()

# Create a new dataset to which we want to load everything. Here we are using the "from_json" method to initialize the complete dataset
dataset = Dataset.from_json("./md_com.json")

# Check if we recorvered the dataset
print(dataset.yaml())

# Upload the dataset
p_id = dataset.upload (dataverse_name="roy_dataverse")
#dataset.update(contact_name="Sarbani Roy", contact_email="sarbani.roy@simtech.uni-stuttgart.de")
print('Dataset created and directory uploaded successfully.')