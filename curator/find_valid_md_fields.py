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
    for key, value in json_data.items():
        if key == class_name and isinstance(value, dict):
            return value
        elif isinstance(value, dict):
            nested_data = get_class_data(value, class_name)
            if nested_data:
                return nested_data
        elif isinstance(value, list):
            for item in value:
                if isinstance(item, dict):
                    nested_data = get_class_data(item, class_name)
                    if nested_data:
                        return nested_data
    return None

# Open the output file in read mode to check if "#Fill with harvested information" exists
with open("curate_for_darus.py") as output_file:
    lines = output_file.readlines()

# Find the index and indent of the line "#Fill with harvested information" in the output file
line_index = None
line_indent = None
for i, line in enumerate(lines):
    if "#Fill with harvested information" in line:
        line_index = i + 1
        line_indent = line.index("#")
        break

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

        #To get the class data corresponding to the class_name from example_json_data       
        #example_class_data = get_class_data(example_json_data, class_name)
        print(class_name)
        #print(example_class_data)

        # Check if the class's "typeClass" attribute is compound
        typeclass = citation_class_data.get("typeClass")
        
        if typeclass == "compound":
            # Construct the line to add with the same indent
            new_line = " " * line_indent + f"citation.add_{class_name}()\n"
            # Insert the new line in the output file after the line "#Fill with harvested information"
            lines.insert(line_index, new_line)
            line_index += 1
        else:
            # Construct the line to add with the same indent
            new_line = " " * line_indent + f"citation.{class_name} = \n"
            # Insert the new line in the output file after the line "#Fill with harvested information"
            lines.insert(line_index, new_line)
            line_index += 1

# Write the updated contents back to the output file
with open("curate_for_darus.py", 'w') as file:
    file.writelines(lines)       
