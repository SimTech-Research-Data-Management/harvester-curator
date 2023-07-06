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

def get_class_data(json_data, class_name):
    class_data = {}

    def extract_attributes(data):
        if isinstance(data, dict):
            for key, value in data.items():
                if isinstance(value, (dict, list)):
                    class_data[key] = value
                else:
                    class_data[key] = value
                extract_attributes(value)

    extract_attributes(json_data)
    return class_data

# Load the citation metadata JSON file
citation_metadata_file = "./metadata_schema_DaRUS/citation.json"
with open(citation_metadata_file) as file:
    citation_metadata = json.load(file)

# Load the example JSON file
example_json_file = "citation_meta_ex.json"
with open(example_json_file) as file:
    example_json_data = json.load(file)

# Get the classes from the example JSON file
example_json_classes = get_json_classes(example_json_data)

# Iterate over the classes in the citation metadata
for class_name in get_json_classes(citation_metadata):
    if class_name in example_json_classes:
        
        #To get the class data corresponding to the class_name from citation_metadata
        citation_class_data = get_class_data(citation_metadata, class_name)
        #print(citation_class_data)
        
        #To get the class data corresponding to the class_name from example_json_data       
        example_class_data = get_class_data(example_json_data, class_name)
        #print(class_name)
        #print(example_class_data)

        # Check if the class's "typeClass" attribute is compound
        typeclass = citation_class_data.get("typeClass")
        print(typeclass)
        
# Print the attribute-value pairs
for attribute, value in example_class_data.items():
    print(f"{attribute}: {value}")        