import json

def get_json_classes(json_data):
    classes = set()

    def extract_classes(data):
        if isinstance(data, dict):
            classes.update(data.keys())
            for value in data.values():
                extract_classes(value)

    extract_classes(json_data)
    return classes

def generate_command(example_json_class_data, class_prop, command):

    for data in example_json_class_data:
        for prop_name, prop_info in class_prop.items():
            if prop_name in data:
                prop_value = data.get(prop_name)
                command = command + f'{prop_name} = "{prop_value}", '

    # Remove the last comma and add closing parenthesis
    command = command[:-2] + ")"

    return command

# Load the example JSON file
example_json_file = "citation_meta_ex.json"
with open(example_json_file) as file:
    example_json_data = json.load(file)

# Get the classes from the example JSON file
example_json_classes = get_json_classes(example_json_data)

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


# the extracted information
for class_name, class_info in classes_info.items():
    if class_name in example_json_classes:
        #get the data of a particular class from the json file of harvested metadata
        example_json_class_data = example_json_data[class_name]

        if class_info['type_class'] == "compound":
            # Get the definitions from the schema
            class_prop = schema.get('definitions', {}).get(class_name, {}).get('properties', {})

            if class_prop:
                command = f"citation.add_{class_name}(" 
                command = generate_command(example_json_class_data, class_prop, command)
                print(command)        
            else:
                print(f'citation.add_{class_name} = "{example_json_class_data}"')

        else:
            #Todo: validate datatype before pushing
            #print(type(example_json_class_data).__name__)
            #print(class_info['type'])
            class_prop = schema.get('definitions', {}).get(class_name, {}).get('properties', {})
            if class_prop:
                command = f"citation.{class_name}("
                command = generate_command(example_json_class_data, class_prop, command)
                print(command)
            else:
                print(f'citation.{class_name} = "{example_json_class_data}"')