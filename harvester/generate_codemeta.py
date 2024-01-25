import requests
import os
import re
import json

def read_install_py(path):

    # print(f"Reading 'install.py' from: {path}")

    with open(path, 'r') as file:
        python_script_content = file.read()

    # Extract the name of 'top'
    top_value = None
    for line in python_script_content.split('\n'):
        if 'top =' in line:
            top_value = line.split('=')[1].strip().strip('"')

    # Check if 'top' value is found
    if top_value:
        name = top_value
        #print(f'Name: {name}')

    
    # Getting dependencies

    software_requirements = []
    code_repository = None
    version = None
    for line in python_script_content.split('\n'):
        # Use regular expression to extract the first argument
        match = re.search(r'installModule\("(.*?)", "(.*?)", "(.*?)"\)', line)
        if match:
            requirements_name = match.group(1)
            requirements_url = match.group(2)
            requirements_version = match.group(3)
            if '/' in requirements_version:
                requirements_version = requirements_version.split('/')[-1]
                software_requirements.append({"name": requirements_name, "version":requirements_version, "info_url": requirements_url})

            # TODO: Change the idea of collecting code_repository
            elif requirements_version == 'main' and requirements_name in name:
                code_repository = requirements_url
                version = requirements_version
            
            else:
                software_requirements.append({"name": requirements_name, "version":requirements_version, "info_url": requirements_url})

            
    #print(f'software_requirements: {software_requirements}')

    
    return (name, software_requirements, code_repository, version)
            
  
def get_gitlab_repo_language(api_url):
    try:
        # Get the GitLab access token from the environment variable
        access_token = os.environ.get('GITLAB_ACCESS_TOKEN')

        if not access_token:
            print("GitLab access token not found. Set the GITLAB_ACCESS_TOKEN environment variable.")
            return None
        
        # Make a request to the GitLab API with the provided access token
        headers = {'Authorization': f'Bearer {access_token}'}
        response = requests.get(api_url, headers=headers)

        languages = []

        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            # Parse the JSON response
            response_json = response.json()

            # Iterate through the dictionary items and append keys to the list
            for key, value in response_json.items():
                languages.append({"name": key, "version": value})

            return languages
        else:
            print(f"Failed to retrieve repository information. Status Code: {response.status_code}")
            print(f"Response Content: {response.text}")
    except Exception as e:
        print(f"An error occurred: {str(e)}")

    return languages


def codemeta_from_install(path):
    
    Install_data = {}

    # Getting name from install.py
    name, software_requirements, code_repository, version = read_install_py(path)
    
    Install_data['name'] = name
    Install_data['code_repository'] = code_repository
    Install_data['version'] = version
    Install_data['software_requirements'] = software_requirements
    
    # will write "programmingLanguage" block in codemeta.json
    
    # TODO: Get id from repo_url 
    # Construct the GitLab API URL for the repository
    code_lang_api_url = "https://git.iws.uni-stuttgart.de/api/v4/projects/834/languages"

    # Get the programming language of the repository
    language = get_gitlab_repo_language(code_lang_api_url)

    if language:
        Install_data['programmingLanguage'] = language
    
    else:
        print("Failed to retrieve repository information.")

    # print(f'CODEMETA:{codemeta_data}')

    return(Install_data)

def codemeta_from_requirements(path):
    #print(f"Found 'requirements.txt' in the first level: {path}") 

    # Read the contents of requirements.txt
    with open(path, 'r') as file:
        requirements_content = file.read()

    # Process each line in the requirements.txt file
    software_requirements = []
    for line in requirements_content.split('\n'):
        # Skip comments and empty lines
        if line.startswith('#') or not line.strip():
            continue
        
        match = re.search(r'(\S+)\s+(\S+)', line)
        if match:
            name = match.group(1)
            version = match.group(2)
            software_requirements.append({"name": name, "version": version})
    # print('\n')
    # print(software_requirements)   
    # print('\n')

    return(software_requirements)


    

def write_codemeta(codemeta_install, codemeta_requirements, path):

    codemeta_data = codemeta_install

    if codemeta_data:
        if codemeta_requirements:
            codemeta_data['software_requirements'].extend(codemeta_requirements)
    
    print(codemeta_data)

    # Write the data to codemeta.json at the first level of the specified path
    codemeta_path = os.path.join(path, 'codemeta.json')
    #print(codemeta_path )

    # Write the data to codemeta.json
    with open(codemeta_path, 'w') as json_file:
        json.dump(codemeta_data, json_file, indent=2)
    
    print("codemeta.json created successfully.")