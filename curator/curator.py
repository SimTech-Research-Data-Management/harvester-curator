import re
import os
import json
import difflib
import requests
import argparse
from pyDaRUS import Dataset, Citation, Privacy, EngMeta, Process, CodeMeta

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
    
def cal_simi_rat(string1, string2):
    sequence_matcher = difflib.SequenceMatcher(None, string1, string2)
    # Note: Perform continuous checking on second string. 
    # Ex: "diet" and "tide" matches "de" but for "tide" and "diet" onlt "t" 
    # as "t" is at the end of "diet", so no continuous match except "t" itself.
    similarity_ratio = sequence_matcher.ratio()
    return similarity_ratio

def find_key_recursive(data, target_key):
    if target_key in data:
        return data[target_key]
    for key, value in data.items():
        if isinstance(value, dict):
            result = find_key_recursive(value, target_key)
            if result:
                return result
    return None

def extract_attri_value_path(data):
    result = []

    def recursive_extract(item, current_key=None, current_path=None):
        if current_path is None:
            current_path = []

        if isinstance(item, dict):
            for key, value in item.items():
                current_path.append(key)
                recursive_extract(value, key, current_path.copy())
                current_path.pop()
        elif isinstance(item, list):
            for i, inner_item in enumerate(item):
                current_path.append(i)
                recursive_extract(inner_item, current_key, current_path.copy())
                current_path.pop()
        else:
            if current_key is not None:
                result.append({
                    'attribute': current_key,
                    'value': item,
                    'path': current_path.copy()
                })

    recursive_extract(data)
    return result

def clean_string(input_string):
    # Check if the input is a string
    if isinstance(input_string, str):
        # Convert the string to lowercase
        cleaned_string = input_string.lower()
        # Remove special characters and spaces
        cleaned_string = re.sub(r'[^a-zA-Z0-9]', '', cleaned_string)
        return cleaned_string
    else:
        # Handle the case where input_string is not a string (e.g., it's an int)
        return str(input_string)

# If we want to put class_name in com_md.json
def find_parent_name(current_data, target_child):
        for key, value in current_data.items():
            if isinstance(value, dict):
                if 'childFields' in value and target_child in value['childFields']:
                    return key
                elif 'items' in value and target_child in value['items']:
                    return key

                result = find_parent_name(value, target_child)
                if result:
                    return result
                
#If we want to put title in com_md.json
# def find_parent_name(current_data, target_child):
#         for key, value in current_data.items():
#             if isinstance(value, dict):
#                 if 'childFields' in value and target_child in value['childFields']:
#                     return value.get('title')
#                 elif 'items' in value and target_child in value['items']:
#                     return value.get('title')

#                 result = find_parent_name(value, target_child)
#                 if result:
#                     return result


def get_matching_md_fields(test_criteria, fields):
    matches = []
    num_matches = 0

    for class_name, class_info in fields.items():
        cleaned_class_name = clean_string(class_name)
        title = class_info.get('title')
        cleaned_title = clean_string(title)

        if cleaned_class_name == cleaned_title:
            current_test_criteria = [cleaned_class_name]
        else:
            current_test_criteria = [cleaned_class_name, cleaned_title]

        # Check if the provided test_criteria matches the current entry
        if test_criteria in current_test_criteria:           
            parent_name = find_parent_name(fields, class_name)
            if parent_name is None and 'childFields' in class_info:
                first_child_field = next(iter(class_info.get('childFields', {})), None)
                parent_name = class_name
                class_name = first_child_field
                
                # parent_name = title
                # # Access the 'childFields' key
                # child_fields = class_info.get('childFields', {})
                # # Get the first child field and its title
                # first_child_field = next(iter(child_fields.values()), None)
                # title_of_first_child = first_child_field.get('title')
                # title = title_of_first_child
            matches.append({
                'class_name': class_name,
                # 'title' : title,
                # 'class_info': class_info,
                'parent': parent_name,
            })
        else:            
            sim_rat_max = 0
            for current_criteria in current_test_criteria:
                sim_rat = cal_simi_rat(test_criteria, current_criteria)
                if sim_rat > sim_rat_max:
                    sim_rat_max = sim_rat
                    if sim_rat_max > 0.85:    
                        parent_name = find_parent_name(fields, class_name)
                        if parent_name is None and 'childFields' in class_info:
                            first_child_field = next(iter(class_info.get('childFields', {})), None)
                            parent_name = class_name
                            class_name = first_child_field                            
                        matches.append({
                            'class_name': class_name,
                            # 'class_info': class_info,
                            'parent': parent_name,
                        })
                        #     parent_name = title
                        #     # Access the 'childFields' key
                        #     child_fields = class_info.get('childFields', {})
                        #     # Get the first child field and its title
                        #     first_child_field = next(iter(child_fields.values()), None)
                        #     title_of_first_child = first_child_field.get('title')
                        #     title = title_of_first_child
                        # matches.append({
                        #     'class_name': class_name,
                        #     'title' : title,
                        #     # 'class_info': class_info,
                        #     'parent': parent_name,
                        # })

    # Include the number of matches in the result
    num_matches = len(matches)
    return num_matches, matches if matches else None

def process_metadata_mapping(har_md_dict, mapping_data):
    image_index = None
    image_value = ""
    del_index = 0
    keys_to_delete = []

    for i, md_entry in enumerate(har_md_dict):
        attri = md_entry['attribute']
        value = md_entry['value']
        path = md_entry['path']

        cleaned_attri = clean_string(attri)

        if path is not None and len(path) >= 2:
            if isinstance(path[-2], int):
                path_index = path[:-1]

        for image, preimages in mapping_data.items():
            num_preimages = len(preimages) - 1
            preimage_index = 0
            for preimage in preimages:
                if clean_string(preimage) == cleaned_attri:
                    if path_index == image_index:
                        attri = image
                        value = image_value + " " + value
                        path = path[:-1] + [attri]
                        keys_to_delete.append(del_index)

                        if preimage_index == num_preimages - 1:
                            mapped_entry = {
                                'attribute': attri,
                                'value': value,
                                'path': path
                            }
                            har_md_dict[i] = mapped_entry

                    image_index = path_index
                    image_value = value
                    del_index = i

    # Delete the entries outside the loop
    # i is introduced to manage the proper order of deletion
    i = 0
    for key in keys_to_delete:
        del har_md_dict[key-i]
        i = i + 1

    return har_md_dict


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

def process_metadata(parent, type_name_value, value, schema_data, index_to_update, schema_name):

    # get the pydarus-compatible class name from type_name
    parent = attribute_name_by_type_name(schema_name, parent)
    type_name_value = attribute_name_by_type_name(schema_name, type_name_value)

    if parent is not None:
        # Create the key in schema_data if it doesn't exist
        if parent not in schema_data:
            schema_data[parent] = []

        # Handle both single values, lists, and dictionaries
        if isinstance(value, list):
            if index_to_update is not None:
                # If an index is specified, add the key-value pair to the specified index within the list
                existing_values = schema_data.get(parent, [])
                if index_to_update < len(existing_values):
                    existing_values[index_to_update].update({type_name_value: value})
                else:
                    # If the index is out of range, append a new dictionary to the list
                    existing_values.append({type_name_value: value})
                schema_data[parent] = existing_values
            else:
                # If no index is specified, append a new dictionary to the list for each item
                list_of_dicts = [{type_name_value: item} for item in value]
                existing_values = schema_data.get(parent, [])
                existing_values.extend(list_of_dicts)
                schema_data[parent] = existing_values

        elif isinstance(value, dict):
            if index_to_update is not None:
                # If an index is specified, add the key-value pair to the specified dictionary
                existing_values = schema_data.get(parent, [])
                existing_values[index_to_update] = value
                schema_data[parent] = existing_values
            else:
                # If no index is specified, append the dictionary directly to the list
                existing_values = schema_data.get(parent, [])
                existing_values.append(value)
                schema_data[parent] = existing_values

        else:
            if index_to_update is not None:
                # If an index is specified, update the existing dictionary with the single value
                existing_values = schema_data.get(parent, [])
                if index_to_update < len(existing_values):
                    existing_values[index_to_update].update({type_name_value: value})
                else:
                    # If the index is out of range, append a new dictionary to the list
                    existing_values.append({type_name_value: value})
                schema_data[parent] = existing_values
            else:
                # If no index is specified, append the single value directly to the list
                schema_data[parent].append({type_name_value: value})
    else:
        if index_to_update is not None:
            if isinstance(value, list) or isinstance(value, dict):
                for val in value:
                    # Add the key-value pair to the specified dictionary at the given index
                    schema_data[type_name_value][index_to_update] = val
            else:
                # Add the key-value pair to the specified dictionary at the given index
                schema_data[type_name_value][index_to_update] = value
        else:
            if isinstance(value, list) or isinstance(value, dict):
                for val in value:
                    schema_data[type_name_value] = val
            else:
                schema_data[type_name_value] = value

def get_compatible_metadatablocks(updated_har_md_dict, com_metadata_file, com_metadata, schema_name):

    # Check if 'metadatablocks' class is present in harvested metadata file
    if 'metadatablocks' not in com_metadata:
        com_metadata['metadatablocks'] = {}

    metadatablocks_data = com_metadata['metadatablocks']
    
    # Check if 'schema_name' is present under 'metadatablocks'
    if schema_name not in metadatablocks_data:
        # Create 'schema_name' as a subclass
        metadatablocks_data[schema_name] = {}
    
    schema_data = metadatablocks_data[schema_name]

    # Generate all fields from metadata schema
    schema_fields = find_key_recursive(metadata_schema, 'fields')

    # Create a list to store metadata entries with no corresponding entry in md_com.json
    unmatched_entries = []

    # processing each attribute in harvested matadata
    for md_entry in updated_har_md_dict:
        attri = md_entry['attribute']
        value = md_entry['value']
        path = md_entry['path']

        # Making attris in lower alphanumeric values
        cleaned_attri = clean_string(attri)

        # Get the parent of harvested metadata attribute
        har_md_parent = None
        if path is not None and len(path) >= 3:
            har_md_parent = path[-3]

        # Get the type name from the metadata schema (if there is any match) corresponding to each key in harvested metadata 
        num_matches, matches = get_matching_md_fields(cleaned_attri, schema_fields)

        com_attri = None
        parent = None
        # num_matches > 0 certifies that there is a corresponding metadata field in the metadata schema
        if num_matches > 0:
            # Access all matches
            for match in matches:
                class_name = match['class_name']
                # title = match['title']
                schema_parent = match['parent']
                if schema_parent is not None:
                    if num_matches == 1:
                        com_attri = class_name
                        #com_attri = title
                        parent = schema_parent
                    if (num_matches > 1):
                        if har_md_parent is not None:
                            sim_rat_max = 0

                            cleaned_har_md_parent = clean_string(har_md_parent)
                            cleaned_schema_parent = clean_string(schema_parent)

                            if cleaned_har_md_parent == cleaned_schema_parent:
                                com_attri = class_name
                                #com_attri = title
                                parent = schema_parent 
                            else:
                                sim_rat = cal_simi_rat(cleaned_schema_parent, cleaned_har_md_parent)
                                if sim_rat > sim_rat_max:
                                    sim_rat_max = sim_rat
                                    if sim_rat_max > 0.85:
                                        com_attri = class_name
                                        #com_attri = title
                                        parent =schema_parent
                        # There is no use-cases so far. May be it is required to change according to 
                        else:
                            sim_rat_max = 0

                            cleaned_schema_parent = clean_string(schema_parent)
                            if cleaned_attri == cleaned_schema_parent:
                                com_attri = class_name
                                #com_attri = title
                                parent = schema_parent 
                            else:
                                sim_rat = cal_simi_rat(cleaned_schema_parent, cleaned_attri)
                                if sim_rat > sim_rat_max:
                                    sim_rat_max = sim_rat
                                    if sim_rat_max > 0.85:
                                        com_attri = class_name
                                        #com_attri = title
                                        parent = schema_parent 
                else:  
                    # data would be added against class_name/title
                    com_attri = class_name
                    #com_attri = title        
   
            # get the index
            index_to_update = None
            if path is not None and len(path) >= 2:
                if isinstance(path[-2], int):
                    index_to_update = path[-2]
            
            # Capitalize the first letter of schema_name
            if schema_name and not schema_name[0].isupper():
                schema_name = schema_name[0].capitalize() + schema_name[1:]


            # Write compatible metadata in the json dictionary
            if com_attri is not None:
                process_metadata(parent, com_attri, value, schema_data, index_to_update, schema_name)
        
        else:
            # No match indicating no corresponding entry in md_com.json
            unmatched_entries.append(md_entry)

    # Write the updated JSON data back to the file
    with open(com_metadata_file, 'w') as json_file:
        json.dump(com_metadata, json_file, indent=2)            

    return unmatched_entries

if __name__ == "__main__":  
   
    # default_darus_metadata_endpoint
    darus_metadata_endpoint = "./api_end_points/darus_md_schema_api_endpoints.json"

    arg_parser = argparse.ArgumentParser(description="Generate compatible metadata.")
    arg_parser.add_argument("--darus", dest="api_endpoints_file_path", default=darus_metadata_endpoint, nargs='?', const=darus_metadata_endpoint, help="API endpoint for metadata.")
    arg_parser.add_argument("--path", dest="har_json_file", required=True, help="Path to the harvested JSON file.")
    # arg_parser.add_argument("-i", "--interactive", action="store_true", help="Enable interactive mode.")

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

    # # Extract metadata for each file
    # har_data = {}
    # for group in har_json_data["groups"]:
    #     for file in group["files"]:
    #         metadata = file.get("metadata")
    #         if metadata:
    #             har_data.update(metadata)

    # Collect all attributes, values, paths from harvested metadata
    har_md_dict = extract_attri_value_path(har_json_data)

    # Read, load and apply the mapping file
    mapping_file = "mapping.json"
    with open(mapping_file, "r") as mapping_file:
        mapping_data = json.load(mapping_file)

    updated_har_md_dict = process_metadata_mapping(har_md_dict, mapping_data)

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
            schema_name = block.get("title")

            if schema_name and api_url:
                metadata_schema = get_json_from_api(api_url)
                print(f"Processing {schema_name} metadata...\n")
                # Search, create, and update corresponding metadata (passing the interactive argument)
                unmatched_har_metadata = get_compatible_metadatablocks(updated_har_md_dict, com_metadata_file, com_metadata, schema_name)
                updated_har_md_dict = unmatched_har_metadata
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