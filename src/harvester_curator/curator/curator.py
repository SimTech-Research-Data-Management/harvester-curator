import re
import os
import json
import difflib
import requests
import argparse
import yaml
import traceback
from pathlib import Path

def load_json_file(filepath):
    try:
        with open(filepath, "r") as f:
            data = json.load(f)
            if data is None or (isinstance(data, (list, dict)) and len(data) == 0):
                raise ValueError(f"Data in {filepath} is None or empty.")
            return data
    except FileNotFoundError:
        print(f"The file {filepath} was not found.")
    except json.JSONDecodeError:
        print(f"Error decoding JSON from {filepath}")
    except Exception as e:
        print(f"An error occured: {e}")
    return None

def get_json_from_api(api_url):
    try:
        response = requests.get(api_url)
        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            # Parse the JSON content
            json_data = response.json()
            return json_data
        else:
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
                

def find_matches(test_criteria, fields):
    matches = []

    for class_name, class_info in fields.items():
        cleaned_class_name = clean_string(class_name)
        title = class_info.get('title')
        cleaned_title = clean_string(title)

        if cleaned_class_name == cleaned_title:
            current_test_criteria = [cleaned_class_name]
        else:
            current_test_criteria = [cleaned_class_name, cleaned_title]

        if 'childFields' in class_info:
            child_fields = class_info['childFields']
            for child_field_class_name, child_field_class_info in child_fields.items():
                cleaned_child_class_name = clean_string(child_field_class_name)
                cleaned_child_title = clean_string(child_field_class_info.get('title', ''))                

                if cleaned_child_class_name == cleaned_child_title:
                    current_child_test_criteria = [cleaned_child_class_name]
                else:
                    current_child_test_criteria = [cleaned_child_class_name, cleaned_child_title]

                # Check if the provided test_criteria matches the current entry
                if test_criteria in current_child_test_criteria: 
                    parent_name = class_name
                    allow_multiple = child_field_class_info.get('multiple')
                        
                    matches.append({
                        'class_name': child_field_class_name,
                        'allow_multiple': allow_multiple,
                        'parent': parent_name,
                    })                        
                # Check if the provided test_criteria matches the main class_name 
                elif test_criteria in current_test_criteria:        
                    parent_name = find_parent_name(fields, class_name)
                    allow_multiple = class_info.get('multiple')
                    if parent_name is None and 'childFields' in class_info:
                        first_child_field = next(iter(class_info.get('childFields', {})), None)
                        parent_name = class_name
                        class_name = first_child_field
                        
                    matches.append({
                        'class_name': class_name,
                        'allow_multiple': allow_multiple,
                        'parent': parent_name,
                    })
                # May be not required
                # else:            
                #     sim_rat_max = 0
                #     for current_criteria in current_test_criteria:
                #         sim_rat = cal_simi_rat(test_criteria, current_criteria)
                #         if sim_rat > sim_rat_max:
                #             sim_rat_max = sim_rat
                #             if sim_rat_max > 0.85:    
                #                 parent_name = find_parent_name(fields, class_name)
                #                 allow_multiple = class_info.get('multiple')
                #                 if parent_name is None and 'childFields' in class_info:
                #                     first_child_field = next(iter(class_info.get('childFields', {})), None)
                #                     parent_name = class_name
                #                     class_name = first_child_field                            
                #                 matches.append({
                #                     'class_name': class_name,
                #                     'allow_multiple': allow_multiple,
                #                     'parent': parent_name,
                #                 })
            #print(f'sim_rat_max: {sim_rat_max}')

        
        elif test_criteria in current_test_criteria:            
            parent_name = find_parent_name(fields, class_name)
            allow_multiple = class_info.get('multiple')
            if parent_name is None and 'childFields' in class_info:
                first_child_field = next(iter(class_info.get('childFields', {})), None)
                parent_name = class_name
                class_name = first_child_field
                
            matches.append({
                'class_name': class_name,
                'allow_multiple': allow_multiple,
                'parent': parent_name,
            })
        # May be not required
        # else:            
        #     sim_rat_max = 0
        #     for current_criteria in current_test_criteria:
        #         sim_rat = cal_simi_rat(test_criteria, current_criteria)
        #         if sim_rat > sim_rat_max:
        #             sim_rat_max = sim_rat
        #             if sim_rat_max > 0.85:    
        #                 parent_name = find_parent_name(fields, class_name)
        #                 allow_multiple = class_info.get('multiple')
        #                 if parent_name is None and 'childFields' in class_info:
        #                     first_child_field = next(iter(class_info.get('childFields', {})), None)
        #                     parent_name = class_name
        #                     class_name = first_child_field                            
        #                 matches.append({
        #                     'class_name': class_name,
        #                     'allow_multiple': allow_multiple,
        #                     'parent': parent_name,
        #                 })
    return matches

def get_matching_md_fields(cleaned_attri, cleaned_attri_and_parent, fields):
    num_matches = 0
    matches = []

    # First, try to find matches using test_criteria
    matches.extend(find_matches(cleaned_attri, fields))

    # If no matches were found using test_criteria, try using cleaned_attri_and_parent
    if not matches and cleaned_attri_and_parent is not None:
        matches.extend(find_matches(cleaned_attri_and_parent, fields))

    # Include the number of matches in the result
    num_matches = len(matches)
    return num_matches, matches if matches else None

                
# def get_matching_md_fields(test_criteria, cleaned_attri_and_parent, fields):
#     matches = []
#     num_matches = 0
#     #cleaned_attri,
#     
#     for class_name, class_info in fields.items():
#         cleaned_class_name = clean_string(class_name)
#         title = class_info.get('title')
#         cleaned_title = clean_string(title)

#         if cleaned_class_name == cleaned_title:
#             current_test_criteria = [cleaned_class_name]
#         else:
#             current_test_criteria = [cleaned_class_name, cleaned_title]

#         # Check if the provided test_criteria matches the current entry
#         if test_criteria in current_test_criteria:           
#             parent_name = find_parent_name(fields, class_name)
#             allow_multiple = class_info.get('multiple')
#             if parent_name is None and 'childFields' in class_info:
#                 first_child_field = next(iter(class_info.get('childFields', {})), None)
#                 parent_name = class_name
#                 class_name = first_child_field
                
#             matches.append({
#                 'class_name': class_name,
#                 'allow_multiple': allow_multiple,
#                 'parent': parent_name,
#             })
#         else:            
#             sim_rat_max = 0
#             for current_criteria in current_test_criteria:
#                 sim_rat = cal_simi_rat(test_criteria, current_criteria)
#                 if sim_rat > sim_rat_max:
#                     sim_rat_max = sim_rat
#                     if sim_rat_max > 0.85:    
#                         parent_name = find_parent_name(fields, class_name)
#                         allow_multiple = class_info.get('multiple')
#                         if parent_name is None and 'childFields' in class_info:
#                             first_child_field = next(iter(class_info.get('childFields', {})), None)
#                             parent_name = class_name
#                             class_name = first_child_field                            
#                         matches.append({
#                             'class_name': class_name,
#                             'allow_multiple': allow_multiple,
#                             'parent': parent_name,
#                         })

#     # Include the number of matches in the result
#     num_matches = len(matches)
#     return num_matches, matches if matches else None

def metadata_mapping(har_md_dict, schema_name,  mapping_data):
    image_index = None
    path_index = None
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

        # Get the parent of harvested metadata attribute
        har_md_parent = None
        if path is not None and len(path) >= 3:
            har_md_parent = path[-3]

        for schema, mapping in mapping_data.items():
            for parent, map in mapping.items():
                if schema_name == schema and parent == har_md_parent: # It is better to match schema_parent. but, how?
                    for image, preimages in map.items():
                        num_preimages = len(preimages) - 1
                        preimage_index = 0
                        for preimage in preimages:
                            if clean_string(preimage) == cleaned_attri:
                                if path_index == image_index:
                                    attri = image
                                    value = image_value + " " + str(value)
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


def process_metadata(parent, type_name_value, value, schema_data, index_to_update, schema_name, allow_multiple):  

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
        schema_data.setdefault(type_name_value, [])

        if index_to_update is not None:
            if allow_multiple == True:
                existing_values = schema_data[type_name_value]

                # Extend the list with None if needed
                while len(existing_values) <= index_to_update:
                    existing_values.append(None)
                    existing_values[index_to_update] = value

                schema_data[type_name_value] = existing_values
            else:
                # Add the key-value pair to the specified dictionary at the given index
                schema_data[type_name_value][index_to_update] = value
        else:
            if allow_multiple == True:
                schema_data[type_name_value].append(value)
            else:
                schema_data[type_name_value] = value


def get_compatible_metadatablocks(updated_har_md_dict, com_metadata_file, com_metadata, schema_name, metadata_schema):

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

        # Attri and parent
        if har_md_parent is not None:
            attri_and_parent = '_'.join([har_md_parent, attri])
            cleaned_attri_and_parent = clean_string(attri_and_parent)
        else:
            cleaned_attri_and_parent = None

        # Get the type name from the metadata schema (if there is any match) corresponding to each key in harvested metadata 
        num_matches, matches = get_matching_md_fields(cleaned_attri, cleaned_attri_and_parent, schema_fields)
        
        com_attri = None
        parent = None
        # num_matches > 0 certifies that there is a corresponding metadata field in the metadata schema
        if num_matches > 0:
            # Access all matches
            for match in matches:
                class_name = match['class_name']
                allow_multiple = match['allow_multiple']
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
                elif isinstance(path[-1], int):
                        index_to_update = path[-1]

            # Capitalize the first letter of schema_name
            if schema_name and not schema_name[0].isupper():
                schema_name = schema_name[0].capitalize() + schema_name[1:]

            # Write compatible metadata in the json dictionary
            if com_attri is not None:
                process_metadata(parent, com_attri, value, schema_data, index_to_update, schema_name, allow_multiple)
        
        else:
            # No match indicating no corresponding entry in md_com.json
            unmatched_entries.append(md_entry)
        
    # Write the updated JSON data back to the file
    with open(com_metadata_file, 'w') as json_file:
        json.dump(com_metadata, json_file, indent=2)            

    return unmatched_entries


def curator(harvester_output_filepath: str, 
            output_filepath: str, 
            api_endpoints_filepath: str
     ) -> None:

    """
    This function compares the harvested metadata with schema-defined metadata from API endpoints, 
    translating and incorporating elements to fill schema fields for API metadata blocks.


    Args:
        harvester_output_filepath: Path of the JSON file with harvested metadata.
        output_filepath: Path of the JSON file to save curated metadata.
        api_endpoints_filepath: Path of the JSON file with schema API endpoints for metadata blocks

    """

    harvester_output_filepath_obj = Path(harvester_output_filepath)
    if not harvester_output_filepath_obj.exists() or harvester_output_filepath_obj.suffix != ".json":
        raise FileNotFoundError(f"Invalid harvester output filepath: '{harvester_output_filepath}' does not exist or is not a .json file.")
    
    api_endpoints_path = Path(api_endpoints_filepath)
    if not api_endpoints_path.exists() or api_endpoints_path.suffix != ".json":
        raise FileNotFoundError(f"Invalid api_endpoints filepath: '{api_endpoints_filepath}' does not exist or is not a .json file.")
  
     # Create the output directory if it does not exists
    output_filepath_obj = Path(output_filepath)
    output_dir_path = output_filepath_obj.parent
  
    if not output_dir_path.exists():
        try:
            output_dir_path.mkdir(parents=True, exist_ok=True)
        except OSError as e:
            raise OSError(f"Output directory '{output_dir_path}' cannot be created. Error: {e}")

     # Check if the parent directory of the output file is a directory
    if not output_dir_path.is_dir():
        raise FileNotFoundError(f"Invalid output directory: The output directory '{output_dir_path}' is not a directory.")

    # Check if the parent directory of the output file is writable
    if not os.access(output_dir_path, os.W_OK):
        raise PermissionError(f"Invalid output directory: The output directory '{output_dir_path}' is not writable.")
    # Check if output_filepath has a .json extension
    if output_filepath_obj.suffix != ".json":
        raise ValueError("Invalid output filepath: The output filename must end with '.json'.")
          
    # Initialize a dict to store curated metadata
    com_metadata = {}

    # Load the harvested JSON file
    har_json_data = load_json_file(harvester_output_filepath)
    
    # Read and load the mapping file
    mapping_filename = "mapping.json"
    mapping_filepath = Path(__file__).parent / mapping_filename
    mapping_data = load_json_file(mapping_filepath)

    # Extract metadata for each file
    for group in har_json_data["groups"]:
        file_group_name = group["file_group_name"]
        for file in group["files"]:
            file_names = [file["file_name"].lower()]
            for file_name in file_names:
                if file_group_name in ["bib files", "cff files"]:    
                    target_schema_names = ["citation"]
                elif "codemeta" in file_name:
                    target_schema_names = ["codeMeta20", "citation"]
                else:
                    target_schema_names = []
            
            metadata = file.get("metadata")
            if metadata:

                # Collect all attributes, values, paths from harvested metadata
                har_md_dict = extract_attri_value_path(metadata)

                api_blocks = load_json_file(api_endpoints_filepath)
               
                if not isinstance(api_blocks, list):
                    print("Error: JSON file should contain a list of API blocks.")

                if target_schema_names:
                    for target_schema_name in target_schema_names:                    
                        for block in api_blocks:
                            api_url = block.get("api_endpoint")
                            schema_name = block.get("name")

                            if schema_name == target_schema_name:                                
                                try:
                                    metadata_schema = get_json_from_api(api_url)
                                    print(f"Processing {schema_name} metadata for {file_name}...\n")

                                    
                                    # Apply the mapping
                                    updated_har_md_dict = metadata_mapping(har_md_dict, schema_name, mapping_data)  
                                    
                                    # Search, create, and update corresponding metadata (passing the interactive argument)
                                    unmatched_har_metadata = get_compatible_metadatablocks(updated_har_md_dict, output_filepath, com_metadata, schema_name, metadata_schema)
                                    har_md_dict = unmatched_har_metadata
                                    
                                except Exception as e:
                                    print(f"An error occurred while processing API endpoints: {e}")
                                    traceback.print_exc()
                else:
                    for block in api_blocks:
                        api_url = block.get("api_endpoint")
                        schema_name = block.get("name")
                        try:
                            metadata_schema = get_json_from_api(api_url)
                            print(f"Processing {schema_name} metadata for {file_name}...\n")

                            # Apply the mapping
                            updated_har_md_dict = metadata_mapping(har_md_dict, schema_name, mapping_data)  
                            
                            # Search, create, and update corresponding metadata (passing the interactive argument)
                            unmatched_har_metadata = get_compatible_metadatablocks(updated_har_md_dict, output_filepath, com_metadata, schema_name, metadata_schema)
                            har_md_dict = unmatched_har_metadata

                        except Exception as e:
                            print(f"An error occurred while processing API endpoints: {e}")
                            traceback.print_exc()
        
    # Convert com_metadata dictionary to YAML format
    yaml_data = yaml.dump(com_metadata)

    # Print the YAML-formatted data
    print(f'Compatible Metadata:\n{yaml_data}')
    print(f"\n\nCurated metadata successfully saved to {output_filepath}\n")

  
    # # Write curated metadata to the specified output file
    # try:
    #     with open(output_file_path, "w") as f:
    #         json.dump(metadata_dict, f, indent=2, allow_nan=True, cls=JsonSerialize)
    #         print(f"\nCurated metadata successfully saved to {output_file_path}\n")
    # except IOError as error:
    #     raise IOError(f"Failed to write to {output_file_path}")
    

# if __name__ == "__main__":  
   
#     curator()