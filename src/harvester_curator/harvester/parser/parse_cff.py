import re
import subprocess
from harvester_curator.harvester.parser.parse_yaml import parse_yaml

def parse_cff(cff_file: str) -> dict:
    """
    This function parses a CFF file to extract metadata

    Args:
        cff_file (str): An input CFF file
        
    Returns:
        meta_dict (dict): A dictionary that contains extracted metadata        
    """      
    command = ["cffconvert", "--validate", "-i", f"{cff_file}"]
    try:
        # Execute the command
        #subprocess.run(command, check=True)
        subprocess.run(command, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        meta_dict = parse_yaml(cff_file)
        if 'type' in meta_dict:
            meta_dict['type_of_work'] = meta_dict['type']
            del meta_dict['type']

        for author in meta_dict['authors']:
            if 'orcid' in author:
                author['authorIdentifierScheme'] = 'ORCID'

                # get orcid_id from url and put it in meta_dict['authorIdentifier']
                orcid_link = author['orcid']
                if re.match(r'\d{4}-\d{4}-\d{4}-\d{3}[0-9X]', orcid_link):
                    author['authorIdentifier'] = orcid_link
                else:
                    pattern = r'(?<=orcid.org/)\d{4}-\d{4}-\d{4}-\d{3}[0-9X]'
                    matches = re.findall(pattern, orcid_link)
                    if matches:
                        author['authorIdentifier'] = matches[0]
                del author['orcid']
                    
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")
        return
    return meta_dict