import json
from pathlib import Path
from easyDataverse import Dataverse

def check_values_exist(data: dict, keys: list) -> tuple:
    """
    This function recursively checks if all values corresponding to the specified keys exist in the data dictionary.

    Args: 
        data (dict): a dictionary 
        keys (list): a list of keys or nested keys

    Returns:
        tuple: A tuple containing a boolean indicating if all values exist and a list of missing keys
    """

    def check_nested_keys(data, nested_keys):
        if not nested_keys:
            return True
        key = nested_keys[0]
        if isinstance(data, dict):
            value = data.get(key)
            if value is not None:
                return check_nested_keys(value, nested_keys[1:])
            else:
                return False
        elif isinstance(data, list):
            return any(check_nested_keys(item, nested_keys[1:]) for item in data)
        else:
            return False
    
    missing_keys = [key for key in keys if not check_nested_keys(data, key.split("/"))]            
    return (not missing_keys, missing_keys)

def dataset_upload(server_url: str, api_token: str, dataverse_id: str, curated_metadata_filepath: str) -> None:
    """
    This function uploads a dataset with curated metadata to a given Dataverse installation 

    Args: 
        curated_metadata_file (str): Path to the JSON file that contains curated metadata 
        server_url (str): Server address
        api_token (str): API token for accessing Dataverse API
        dataverse_id (str): Alias of the host Dataverse for the dataset to be uploaded

    """
    # Check if curated metadata file exists and has content
    curated_metadata_filepath_obj = Path(curated_metadata_filepath)
    if curated_metadata_filepath_obj.exists() and curated_metadata_filepath_obj.stat().st_size > 0:
        # Open the JSON file for reading
        with open(curated_metadata_filepath, 'r') as json_file:
            # Load the JSON data into a Python dictionary
            curated_metadata = json.load(json_file)
    else:
        # If the file doesn't exist or is empty, initialize an empty dictionary
        raise ValueError(f"{curated_metadata_filepath} does not exist or is empty")

    # Check if citation is among the metadatablocks:
    citation_metadata = curated_metadata.get("metadatablocks").get("citation", {})
    print(f"\n\ncitation metadata: {citation_metadata}")

    if citation_metadata:
        # Check if all required fields for DaRUS citation blocks are filled (datasetContact/datasetContactName is not required by DaRUS but by Jan's code)
        dv_required_fileds = ["title", "author/authorName", "datasetContact/datasetContactName", 
            "datasetContact/datasetContactEmail", "dsDescription/dsDescriptionValue", "subject"]
        all_exist, missing_fields = check_values_exist(citation_metadata, dv_required_fileds)
        
        # Fill in blanks in required fields (for testing dataset uploading only!)
        if missing_fields:
            dict_addition = {}
            for field in missing_fields:
                temp_dict = dict_addition
                keys = field.split("/")
                for key in keys[:-1]:
                    temp_dict = temp_dict.setdefault(key, {})
                if keys[-1] == "subject":
                    temp_dict[keys[-1]] = "Other"
                elif keys[-1] == "datasetContactEmail":
                    temp_dict[keys[-1]] = "unkown@unkown.com"
                else:
                    temp_dict[keys[-1]] = "unkown"

            merged_dict = {}
            for key, value in dict_addition.items():
                merged_dict.setdefault(key, []).append(value)
            
            curated_metadata.get("metadatablocks").get("citation", {}).update(merged_dict)
            missing_fields = []     
                
        if not missing_fields:
            # Initialize Dataverse instance
            dataverse = Dataverse(
                server_url=server_url,
                api_token=api_token,
            )

            codemeta_metadata = curated_metadata.get("metadatablocks").get("codeMeta20", None)  
            if codemeta_metadata: 
                # Note: currently the uploading of metadata does not work when codeMeta20 metablock contains codeRepository and contIntegration 
                # due to occurrence of "TypeError: Object of type Url is not JSON serializable" when codeMeta20 exists
                # So these two fields are removed before metadata uploading   
                codemeta_metadata.pop("codeRepository", None)
                codemeta_metadata.pop("contIntegration", None)
                curated_metadata.get("metadatablocks").update({"codeMeta20": codemeta_metadata})              
           
            # If uploading to demo dataverse, remove codeMeta20 metablock if it exists in curated metadata (demo dataverse does not have codeMeta20 metablock)
            if "demo.dataverse.org" in server_url:        
                codemeta_metadata = curated_metadata.get("metadatablocks").get("codeMeta20", None)  
                if codemeta_metadata: 
                    del curated_metadata["metadatablocks"]["codeMeta20"]
       
            # Load dataset with curated metadata 
            dataset = dataverse.dataset_from_json_string(json.dumps(curated_metadata, indent=2))
                    
            # Upload to the target dataverse collection
            dataset.upload(dataverse_name=dataverse_id)
        
        else:
            error_message = "".join([
                "Missing entries for the required fileds in citation metablocks: ",
                f"{'; '.join(missing_fields)}. ", 
                f"\nPlease make sure that all required fields for citation metablocks are filled before uploading the dataset."
            ])
            raise ValueError(error_message)
    else:
        raise ValueError("Missing citation metablock in dataset metadata")
 

# if __name__ == "__main__":  

#     curator_output_filename = "md_com.json"
#     # File path of the curator generated json file 
#     curated_metadata_file = join(dirname(dirname(abspath(__file__))), "example", curator_output_filename)
 
#     # server_url = "https://demo.dataverse.org"
#     # api_token = ""
#     # dataverse_id = ""

#     server_url = "https://darus.uni-stuttgart.de/"
#     api_token = ""
#     dataverse_id = ""

#     dataset_upload(curated_metadata_file, server_url, api_token, dataverse_id)
