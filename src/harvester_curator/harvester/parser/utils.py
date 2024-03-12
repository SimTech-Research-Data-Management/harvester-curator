import requests
import json
import re
from typing import Union, Any, Dict, Optional, List
from jsonschema import validate

def validate_json(json_file: str) -> Union[Dict[str, Any], bool]:
        """
        This function validates a JSON file

        Args:
            json_file (str): Path to the JSON file to validate

        Returns:
            Union[Dict[str, Any], bool]: If the JSON file is valid, returns the parsed JSON data;
                If the JSON file is invalid or encounters any error during validation, returns False.
        """
        try:
            with open(json_file, 'r') as f:
                json_data = json.load(f)
            return json_data
        except json.JSONDecodeError as e:
            print(f"Invalid JSON format: {e}.")
            return False
        except FileNotFoundError:
            print(f"The file {json_file} was not found.")
            return False
        except PermissionError:
            print(f"Permission denied to access the file {json_file}.")
            return False
        except IOError as e:
            print(f"I/O error occurred: {e}.")
            return False

def get_json_from_url(url: str) -> Optional[Union[Dict[str, Any], bool]]:
    """
    This function fetchs JSON data from a URL

    Args:
        url (str): The URL to fetch JSON data from

    Returns:
        Optional[Union[Dict[str, Any], bool]]: The parsed JSON data if fetching is successful, or False if an error occurs
    """
    try: 
        request_response = requests.get(url, timeout=15)
        request_response.raise_for_status()
        json_data = request_response.json()
        return json_data
    except requests.exceptions.HTTPError as http_err: 
        raise ValueError(f"HTTP Error for URL '{url}': {http_err.args[0]}.") 
    except requests.exceptions.ReadTimeout as timeout_err:
        raise TimeoutError(f"Timeout Error for URL '{url}'.") 
    except requests.exceptions.ConnectionError as con_err: 
        raise ConnectionError(f"Connection Error for URL '{url}'.") 
    except requests.exceptions.RequestException as exe_rr: 
        raise RuntimeError(f"Request Exception for URL '{url}': {exe_rr}.")
    return False

def validate_jsonld(json_data: Dict[str, Any], jsonld_schema: Dict[str, Any]) -> bool:
    """
    This function validates JSON-LD data against a JSON-LD schema

    Args:
        json_data (Dict[str, Any]): JSON-LD data to validate
        jsonld_schema (Dict[str, Any]): JSON-LD schema to validate against

    Returns:
        bool: True if the JSON-LD data is valid against the schema, Falls otherwise

    """
    try:
        # Validate JSON-LD data against JSON-LD schema
        validate(instance=json_data, schema=jsonld_schema)
        return True
    except json.JSONDecodeError as e:
        print(f"Invalid JSON format: {e}.")
        return False
    except KeyError as e:
        print(f"Key error: {e}.")
        return False
    except Exception as e:
        print(f"An error occurred: {e}.")
        return False
    
def remove_keys_with_prefix(data: Union[Dict[str, Any], list], prefix: str, exclude_key: List[str]) -> Union[Dict[str, Any], list, Any]:
    """
    This function recursively removes key-value pairs from JSON data where the key starts with a speficic prefix

    Args:
        data (Union[Dict[str, Any], list]): data to filter
        prefix (str): The prefix to check for

    Returns:
        Union[Dict[str, Any], list, Any]: The filtered data
    """

    if isinstance(data, dict):
        return {
            "id" if key == "@id" else key: remove_keys_with_prefix(value, prefix, exclude_key)
            for key, value in data.items()
            if (not key.startswith(prefix)) or key in exclude_key
        }
    elif isinstance(data, list):
        return [remove_keys_with_prefix(item, prefix, exclude_key) for item in data]
    else:
        return data

def extract_info(data: Union[Dict[str, Any], Any], keys: list) -> list:
    """
    This function recursively extracts information from nested dictionaries.

    Args:
        data (Union[Dict[str, Any], Any]): The data to extract information from.
        keys (list): The keys to search for in the data.

    Returns:
        list: A list of extracted information.
    """
    info = []

    def recursive_extract(data):
        if isinstance(data, dict):
            for key, value in data.items():
                if key in keys:
                    info.append(value) 
                    break            
                else:
                    recursive_extract(value)
        elif isinstance(data, list):
            for item in data:
                recursive_extract(item)

    recursive_extract(data)
    return info

def format_author(author: Dict[str, Any], author_role: Union["author", "contributor", "maintainer", "copyrightHolder"]) -> Dict[str, Any]:
    """
    This function formats author information based on author_role (from codemeta file)
    
    Args:
        author (Dict[str, Any]): A dictionary that contains author info such as name, email, id, etc
        author_role (str): Role can be one among author, contributor, maintainer, and copyrightHolder

    Returns:
        author_info (Dict[str, Any]): formatted author information
    """
    given_name = extract_info(author, ["givenName", "given_name", "given-name"])
    family_name = extract_info(author, ["familyName", "family_name", "family-name"])
    email = extract_info(author, ["email", "Email"])
    id_ = extract_info(author, ["id", "identifier", "ID", "Identifier"])

    author_info = {}
    if given_name or family_name:
        author_info[author_role+"Name"] = " ".join(filter(None, family_name + given_name)).strip()
    if email:
        author_info[author_role+"Email"] = " ".join(filter(None, email)).strip()
    if id_:
        # check if id is ORCID iD URL
        id = " ".join(filter(None, id_)).strip()
        orcid_url_pattern = r'^https?://(www\.)?orcid\.org/(\d{4}-){3}\d{3}(\d|X)$'
        if re.match(orcid_url_pattern, id):
            id_number = id.split("/")[-1]
            author_info[author_role+"IdentifierScheme"] = "ORCID"
            author_info[author_role+"Identifier"] = id_number

    return author_info

def process_authors(authors: Union[Dict[str, Any], List[Dict[str, Any]]], author_role: Union["author", "contributor", "maintainer", "copyrightHolder"]) -> List[Dict[str, Any]]:
    """
    This function formats a list of dictionaries or a single dictionary that contains author(s) information based on author_role (from codemeta file)

    Args:
        authors (Union[Dict[str, Any], List[Dict[str, Any]]]): A list of dictionaries or a signle dictionary that contains author(s) information such as name, email, id, etc
        author_role (str): Role can be one among author, contributor, maintainer, and copyrightHolder. 

    Returns:
        author_list (List[Dict[str, Any]]): 
    """
    if not isinstance(authors, list):
        authors = [authors]

    author_list: List[Dict[str, Any]] = []
    for author in authors:
        formatted_author = format_author(author, author_role)
        author_list.append(formatted_author)
    return author_list


def format_software_info(software_requirement_suggestion: Dict[str, Any], indicator: Union["Requirements", "Suggestions"]) -> Dict[str, Any]:
    """
    This function formats software requirement information (from codemeta file)
    
    Args:
        software_requirement_suggestion (Dict[str, Any]): A dictionary that contains software requirement or suggestion info such as name, version, info url, etc
        indicator: This indicates the types of software info and the value is limited to be either Requirements or Suggestions. 

    Returns:
        software_info (Dict[str, Any]): formatted software info
    """
    
    name = extract_info(software_requirement_suggestion, ["Name", "name"])
    version = extract_info(software_requirement_suggestion, ["Version", "version"])
    info_urls = extract_info(software_requirement_suggestion, ["info_url", "info-url", "infoURL", "sameAs"])
    download_urls = extract_info(software_requirement_suggestion, ["download_url", "download-url", "downloadURL", "sameAs"])
    
    software_info = {}
    if name or version:
        software_info["".join(["software", indicator])] = " ".join(filter(None, name + version)).strip()
    if info_urls:
         software_info["".join(["software", indicator, "InfoUrl"])]= " ".join(filter(None, info_urls)).strip()
    if download_urls:
         software_info["".join(["software", indicator, "Url"])]= " ".join(filter(None, info_urls)).strip()
  
    return software_info

def verify_simulation_data(valid_json_result, filename):
    """
    Function to verify if the JSON data contains simulation data.

    Args:
    - valid_json_result: The JSON data to be verified.

    Returns:
    - True if the JSON file contains simulation data, False otherwise.
    """
    try:
        # Recursive function to traverse the JSON data
        def extract_no_of_numerical_values(data):
            count = 0
            numeric_value_count = 0

            def recursive_extract(item, current_key=None):
                nonlocal count, numeric_value_count

                if isinstance(item, dict):
                    for key, value in item.items():
                        recursive_extract(value, key)
                elif isinstance(item, list):
                    for inner_item in item:
                        recursive_extract(inner_item, current_key)
                else:
                    if current_key is not None and count < 5:
                        count += 1
                        if isinstance(item, (int, float)):
                            numeric_value_count += 1

            recursive_extract(data)
            return numeric_value_count

        # Counter for numerical values encountered
        numerical_values_count = extract_no_of_numerical_values(valid_json_result)

        # Verify if at least two numerical values are encountered
        if numerical_values_count >= 3:
            return True
        else:
            return False
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return False

