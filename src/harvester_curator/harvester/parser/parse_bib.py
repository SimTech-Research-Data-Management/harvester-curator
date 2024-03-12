import re
import subprocess

def parse_bib(bib_file: str) -> dict:
    """
    This function parses a BibTex file to extract metadata

    Args:
        bib_file (str): An input BibTex file
        
    Returns:
        meta_dict (dict): A dictionary that contains extracted metadata        
    """      
    meta_dict = {} 
    with open(bib_file, 'r') as file:

        try:
            bibtex_str = file.read()
            current_entry = {}

            lines = bibtex_str.split('\n')

            for line in lines:
                line = line.strip()

                if not line:
                    continue

                if line.startswith('@'):
                    if current_entry:
                        # Convert the author string to a list of dictionaries
                        if 'author' in current_entry:
                            authors = current_entry['author'].split(' and ')
                            current_entry['author'] = [{'name': author.strip()} for author in authors]

                        # Add the current entry to meta_dict
                        for key, value in current_entry.items():
                            meta_dict.setdefault(key, value)
                            
                        current_entry = {}

                    entry_match = re.match(r'@(\w+){(.*),', line)
                    if entry_match:
                        entry_type, key = entry_match.groups()
                else:
                    value_match = re.match(r'\s*([^=]*)\s*=\s*{(.*)},?', line)
                    if value_match:
                        key, value = value_match.groups()
                        current_entry[key.strip()] = value.strip()

            if current_entry:
                # Convert the author string to a list of dictionaries
                if 'author' in current_entry:
                    authors = current_entry['author'].split(' and ')
                    current_entry['author'] = [{'name': author.strip()} for author in authors]

                # Add the current entry to meta_dict
                for key, value in current_entry.items():
                    meta_dict.setdefault(key, value)
                    
        except subprocess.CalledProcessError as e:
            print(f"Error: {e}")
            return
        
        # print(meta_dict)

    return meta_dict