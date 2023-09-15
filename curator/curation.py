import json
from pyDaRUS import Dataset, Citation, Privacy
from pyDaRUS.metadatablocks.citation import SubjectEnum


def get_json_classes(json_data):
    classes = set()

    def extract_classes(data):
        if isinstance(data, dict):
            classes.update(data.keys())
            for value in data.values():
                extract_classes(value)

    extract_classes(json_data)
    return classes

def generate_commands(json_data, schema):
    commands = []

    def extract_properties(class_name, class_data):
        class_prop = schema.get('definitions', {}).get(class_name, {}).get('properties', {})
        if class_prop:
            command = f"citation.add_{class_name}("
            for prop_name, prop_info in class_prop.items():
                if prop_name in class_data:
                    prop_value = class_data.get(prop_name)
                    command = command + f'{prop_name} = "{prop_value}", '
            command = command[:-2] + ")"
            commands.append(command)
        else:
            command = f'citation.{class_name} = "{class_data}"'
            commands.append(command)

    example_json_classes = get_json_classes(json_data)

    for class_name, class_info in classes_info.items():
        if class_name in example_json_classes:
            example_json_class_data = example_json_data[class_name]
            if class_info['type_class'] == "compound":
                for data in example_json_class_data:
                    extract_properties(class_name, data)
            else:
                extract_properties(class_name, example_json_class_data)

    return commands

# Load the example JSON file
example_json_file = "citation_meta_ex.json"
with open(example_json_file) as file:
    example_json_data = json.load(file)

citation_metadata_file = "./metadata_schema_DaRUS/citation.json"
# Load the JSON schema
with open(citation_metadata_file, 'r') as schema_file:
    schema = json.load(schema_file)

# Get the properties from the schema
properties = schema.get('properties', {})

# Extract classes and their corresponding 'type' and 'type class' from 'properties'
classes_info = {}
for class_name, class_info in properties.items():
    class_type = class_info.get('type')
    class_type_class = class_info.get('typeClass')
    classes_info[class_name] = {'type': class_type, 'type_class': class_type_class}

# Initialize the dataset
dataset = Dataset()

# Initialize metadatablock
citation = Citation()
privacy = Privacy()

# Fill in citation relevant fields
citation.subject = [SubjectEnum.mathematical__sciences]

# Generate commands
commands = generate_commands(example_json_data, schema)

# Execute the commands
for command in commands:
    try:
        exec(command)
        #print(f"Executed: {command}")
    except Exception as e:
        print(f"Failed to execute: {command}")
        print(f"Error: {e}")

# Fill in privacy relevant fields
privacy.personal_data = "no"

# Add each metadatablock to the dataset
dataset.add_metadatablock(citation)
dataset.add_metadatablock(privacy)

# Upload the dataset
p_id = dataset.upload (dataverse_name="roy_dataverse")
#dataset.update(contact_name="Sarbani Roy", contact_email="sarbani.roy@simtech.uni-stuttgart.de")
print('Dataset created and directory uploaded successfully.')