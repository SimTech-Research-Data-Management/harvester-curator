import os
import re
from harvester_curator.harvester.parser.utils import verify_simulation_data, validate_json, get_json_from_url, validate_jsonld, remove_keys_with_prefix, format_author, process_authors, format_software_info


def parse_json(json_file: str) -> dict:
        """
        This function parses a JSON file to extract metadata

        Args:
            json_file (str): Path to the input JSON file
          
        Returns:
            meta_dict (dict): A dictionary that contains extracted metadata        
        """ 
        filename = os.path.basename(json_file).lower()
        if filename == 'harvested_output.json':
            meta_dict = {}

        else:
            try:    
                valid_json_result = validate_json(json_file)
                if valid_json_result:
                    # Check if the JSON file is a codemeta file
                    if "codemeta" in filename and "codemeta.jsonld" not in filename:
                        codemeta_context_url = "https://raw.githubusercontent.com/codemeta/codemeta/master/codemeta.jsonld"
                        codemeta_context = get_json_from_url(codemeta_context_url)
                        if codemeta_context:
                            valid_jsonld_result = validate_jsonld(valid_json_result, codemeta_context)
                            if valid_jsonld_result:
                                filtered_codemeta_data = remove_keys_with_prefix(valid_json_result, "@", ["@id"])
                                # print(f"filtered_codemeta_data: {filtered_codemeta_data}")

                                author_keys_to_process = ["author", "contributor", "maintainer", "copyrightHolder"]
                                for key in author_keys_to_process:
                                    value = filtered_codemeta_data.get(key, {})
                                    if value: 
                                        filtered_codemeta_data[key] = process_authors(value, key)

                                software_requirement_suggestions_indicators = ["Requirements", "Suggestions"]
                                for indicator in  software_requirement_suggestions_indicators: 
                                    software_keys = ["software" + indicator, "software-" + indicator.lower(), "software_" + indicator.lower()]
                                    software_infos = [filtered_codemeta_data.get(key, {}) for key in software_keys]
                                    software_infos = list(filter(None, software_infos))

                                    if software_infos:
                                        software_infos = software_infos[0]
                                        software_info_list = []
                                        if isinstance(software_infos, dict):
                                            software_infos = software_infos.items()
                                        for software_info in software_infos:    
                                            if isinstance(software_info, tuple):
                                                software_info = {software_info[0]:software_info[1]}
                                            software_info_list.append(format_software_info(software_info, indicator))

                                        software_info_list = list(filter(None, software_info_list))
                                        filtered_codemeta_data["".join(["software", indicator, "Item"])] = software_info_list
                                        for key in software_keys: 
                                            filtered_codemeta_data.pop(key, None)
                                
                                # Check if development status is repo status url and then format it into valid input if ncessary
                                repostatus_url_pattern = re.compile(r'^https?://www\.repostatus\.org/#.+')
                                
                                DEVELPMENT_STATUS_INPUT = ["Concept", "WIP", "Active", "Inactive", "Unsupported", "Moved", "Suspended", "Abandoned"]

                                development_status = filtered_codemeta_data.get("developmentStatus")

                                if development_status and repostatus_url_pattern.match(development_status):
                                    filtered_codemeta_data["developmentStatus"]= development_status.split("#")[-1].capitalize()
                            
                                if filtered_codemeta_data.get("developmentStatus") not in DEVELPMENT_STATUS_INPUT:
                                    filtered_codemeta_data.pop("developmentStatus", None)
                                
                                meta_dict = filtered_codemeta_data
                            else:
                                print(f"Faild to validate {json_file} against JSONLD schema {codemeta_context_url}")
                                meta_dict = {}

                        else:
                            print(f"Failed to fetch codemeta context from URL {codemeta_context_url}")                    
                            meta_dict = {}            
                    elif verify_simulation_data(valid_json_result, filename) is True:              
                        min_max_values = {} 
                        for dataset, dataset_value in valid_json_result.items():
                            for variable, value in dataset_value.items():
                                if not isinstance(value, str) and variable.lower() != 'number':                            
                                    if not isinstance(value, list):
                                        min_val, max_val = min_max_values.get(variable, (float('inf'), float('-inf')))
                                        min_val = min(min_val, value)
                                        max_val = max(max_val, value)
                                        min_max_values[variable] = (min_val, max_val)
                                    elif isinstance(value, list) and len(value) == 2 and not any(isinstance(item, list) for item in value):
                                        for i, val in enumerate(value, start=1):        
                                            variable_name = f"{variable}_{'x' if i == 1 else 'y'}"
                                            min_val, max_val = min_max_values.get(variable_name, (float('inf'), float('-inf')))
                                            min_val = min(min_val, val)
                                            max_val = max(max_val, val)
                                            min_max_values[variable_name] = (min_val, max_val)    
                        if min_max_values:
                            meta_dict = {"engMetaMeasuredVar": []}

                            for variable, (min_val, max_val) in min_max_values.items():
                                meta_dict["engMetaMeasuredVar"].append({
                                    "engMetaMeasuredVarName": variable,
                                    "engMetaMeasuredVarValueFrom": min_val,
                                    "engMetaMeasuredVarValueTo": max_val
                                })

                        else:
                            print(f"Failed to fetch min_max_value from simulation data in {filename}")
                            meta_dict = {}
                    else:
                        meta_dict = valid_json_result
                else:
                    print("Failed to validate JSON file: {json_file}")  
                    meta_dict = {}
            except Exception as e:
                print(f"An error occurred: {str(e)}")
                meta_dict = {}
        return meta_dict