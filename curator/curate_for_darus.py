from pyDaRUS import Dataset, Citation, Privacy
from pyDaRUS.metadatablocks.citation import SubjectEnum
#from pyDataverse.api import NativeApi
#import json

def create_dataset():

    #json_file_path = '/home/sarbani/darus_data_harvester/harvester/harvester_output.json'
    #with open(json_file_path, 'r') as file:
    #    dataset_metadata = json.load(file)
    #api = NativeApi(BASE_URL, API_TOKEN)
    #resp = api.create_dataset(DV_PARENT_ALIAS, dataset_metadata)
    #print('Dataset created and directory uploaded successfully.')
    #print(resp)

    # Get user input for Dataverse URL and API token
    #base_url = input("Enter the Dataverse URL: ")
    #api_token = input("Enter the API token: ")

    # Get user input for dataset title and directory path
    #dataset_title = input("Enter the dataset title: ")
    #directory_path = input("Enter the directory path: ")

    # Initialize the dataset
    dataset = Dataset()

    # Initialize metadatablock
    citation = Citation()
    privacy = Privacy()

    # Fill in citation relevant fields
    citation.title = "Curation Test"
    citation.subject = [SubjectEnum.mathematical__sciences]

    # Use add function to append compound objects without having to import the corresponding class
    citation.add_description(text="Testing", date="2023")
    citation.add_author(name="Sarbani Roy", affiliation="SimTech")
    citation.add_contact(name="Sarbani Roy", email="sarbani.roy@simtech.uni-stuttgart.de")

    # Fill in privacy relevant fields
    privacy.personal_data = "no"

    # Add each metadatablock to the dataset
    dataset.add_metadatablock(citation)
    dataset.add_metadatablock(privacy)

    # Upload the dataset
    p_id = dataset.upload (dataverse_name="roy_dataverse")
    #dataset.update(contact_name="Sarbani Roy", contact_email="sarbani.roy@simtech.uni-stuttgart.de")
    print('Dataset created and directory uploaded successfully.')


# Call the fun
#BASE_URL = "https://demodarus.izus.uni-stuttgart.de"
#API_TOKEN = "a7a7e68e-2129-41b6-b6a4-b156cd3a120f"
#DV_PARENT_ALIAS = "roy_dataverse"
create_dataset()
