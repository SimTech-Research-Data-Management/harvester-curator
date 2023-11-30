import json
import os
from pyDaRUS import Dataset, Citation, Privacy, EngMeta 
import requests
import difflib
import argparse

def cal_simi_rat(string1, string2):
    sequence_matcher = difflib.SequenceMatcher(None, string1, string2)
    # Note: Perform continuous checking on second string. 
    # Ex: "diet" and "tide" matches "de" but for "tide" and "diet" onlt "t" 
    # as "t" is at the end of "diet", so no continuous match except "t" itself.
    similarity_ratio = sequence_matcher.ratio()
    return similarity_ratio


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


def attribute_name_by_type_name(cls, type_name):
    if isinstance(cls, str):
        # If cls is a string, assume it's the name of the Pydantic model class
        cls = globals().get(cls, None)
        assert cls is not None, f"Class with name {cls} not found in globals"

    assert hasattr(cls, "__fields__"), (
        f"Object {type(cls)} is not compliant"
    )
    
    for attr in cls.__fields__.values():
        extra_infos = attr.field_info.extra
        
        if type_name == extra_infos["typeName"]:
            return attr.name
        
        if hasattr(attr.type_, "__fields__"):
            res = attribute_name_by_type_name(attr.type_, type_name)
            
            if res is not None:
                return res



def get_compatible_metadatablocks(com_metadata_file, json_data, schema_name, har_json_data, metadata_schema, interactive=False):
    
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
        title = class_info.get('title')
        title_mod = title.replace(' ', '_').lower()
        class_name_mod = class_name.replace(' ', '_').lower()

        test_criterias = [class_name, class_name_mod, title, title_mod]
        type_name = None
        match_found = False

        # Matches the clsses between harvested_data (given as input) and metadata schema.
        for test_criteria in test_criterias:
            if test_criteria in har_json_classes:
                type_name = class_name
                har_class_name = test_criteria
                #print(class_name)
                match_found = True
                break # without this break engMeta match was not working. Do not know why.

        if interactive:
            # If no matches found try to find matches with interactive session     
            if not match_found:
                for har_json_class in har_json_classes:
                    for test_criteria in test_criterias:
                        sim_rat = cal_simi_rat(test_criteria, har_json_class)
                        if sim_rat > 0.85:
                            valid_input = False
                            while valid_input is not True:
                                #per = sim_rat*100
                                #print(f'\nSimilarity matching between {test_criteria} and {har_json_class} is {per}%')
                                user_input = input(f'\nDo you want to mean {test_criteria} by {har_json_class}? (yes/no) \n')
                                if user_input.lower() == "yes":
                                    print(f'{har_json_class} is mapped to {test_criteria}\n')
                                    type_name = class_name
                                    har_class_name = har_json_class 
                                    match_found = True
                                    valid_input = True
                                    break  # Exit the loop if a match is found
                                elif user_input == "no":
                                    print("\nMatching skipped\n")
                                    valid_input = True
                                else:
                                    print("\nInvalid input. Please enter 'yes' or 'no'.\n")
        
        if type_name is not None:
            if schema_name and not schema_name[0].isupper():
            # Capitalize the first letter
                schema_name = schema_name[0].capitalize() + schema_name[1:]

            # get the darus-compatible class name from type_name
            pydarus_class_name = attribute_name_by_type_name(schema_name, type_name)
            har_json_class_data = har_json_data[har_class_name]
            class_child_fields = class_info.get('childFields')
            
            if class_child_fields:
                schema_data[pydarus_class_name] = []
                for data in har_json_class_data:
                    schema_data[pydarus_class_name].append(data)
            else:
                schema_data[pydarus_class_name] = har_json_class_data
            

    # Write the updated JSON data back to the file
    with open(com_metadata_file, 'w') as json_file:
        json.dump(json_data, json_file, indent=2)

if __name__ == "__main__":

    # default_darus_metadata_endpoint
    darus_metadata_endpoint = "./api_end_points/darus_md_schema_api_endpoints.json"

    arg_parser = argparse.ArgumentParser(description="Generate compatible metadata.")
    arg_parser.add_argument("--darus", dest="api_endpoints_file_path", default=darus_metadata_endpoint, nargs='?', const=darus_metadata_endpoint, help="API endpoint for metadata.")
    arg_parser.add_argument("--path", dest="har_json_file", required=True, help="Path to the harvested JSON file.")
    arg_parser.add_argument("-i", "--interactive", action="store_true", help="Enable interactive mode.")

    args = arg_parser.parse_args()

    # File to write compatible metadata
    com_metadata_file = os.path.join(os.path.dirname(args.har_json_file), "curator_output", "md_com.json")

    # Create 'md_com.json' with initial data if it doesn't exist
    if os.path.exists(com_metadata_file):
        with open(com_metadata_file, 'w') as file:
            pass

    initial_data = {"lib_name": "pyDaRUS"}
    with open(com_metadata_file, 'w') as json_file:
        json.dump(initial_data, json_file, indent=2)

    with open(com_metadata_file) as json_file:
        com_metadata = json.load(json_file)

    # Load the harvested JSON file
    with open(args.har_json_file) as file:
        har_json_data = json.load(file)

    try:
        # If --darus is specified without an argument, use the default_darus_file
        if args.api_endpoints_file_path is None:
            args.api_endpoints_file_path = darus_metadata_endpoint

        with open(args.api_endpoints_file_path) as json_file:
            api_blocks = json.load(json_file)

        if not isinstance(api_blocks, list):
            print("Error: JSON file should contain a list of API blocks.")

        for block in api_blocks:
            api_url = block.get("api_endpoint")
            schema_name = block.get("name")

            if schema_name and api_url:
                metadata_schema = get_json_from_api(api_url)
                print(f"Processing {schema_name} metadata...\n")
                # Search, create, and update corresponding metadata (passing the interactive argument)
                com_har_metadata = get_compatible_metadatablocks(com_metadata_file, com_metadata, schema_name, har_json_data, metadata_schema, interactive=args.interactive)

            else:
                print("Error: Each block should contain a metadata schema 'name' and its 'api_endpoint'.")

    except Exception as e:
        print(f"An error occurred while processing API endpoints: {e}")


    # A dataset will be created from the harvested information
    # Initialize dataset
    dataset = Dataset()

    # Create a new dataset to which we want to load everything. Here we are using the "from_json" method to initialize the complete dataset
    dataset = Dataset.from_json(com_metadata_file)

    # Check if we recovered the dataset
    print(dataset.yaml())

    # Upload the dataset
    # p_id = dataset.upload (dataverse_name="roy_dataverse")
    # dataset.update(contact_name="Sarbani Roy", contact_email="sarbani.roy@simtech.uni-stuttgart.de")
