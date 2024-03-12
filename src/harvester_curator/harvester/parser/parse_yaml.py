import yaml

def parse_yaml(yaml_file: str) -> dict:
    """
    This function parses an yaml file to extract metadata

    Args:
        yaml_file (str): An input yaml file
        
    Returns:
        meta_dict (dict): A dictionary that contains extracted metadata        
    """      
    with open(yaml_file, 'r') as yaml_file:
        try:
            meta_dict = yaml.safe_load(yaml_file)
        except yaml.YAMLError as e:
            print(f"Error loading YAML: {e}")
            return {}

    return meta_dict