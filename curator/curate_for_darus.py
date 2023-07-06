from pyDaRUS import Dataset, Citation, Privacy

def create_dataset():

    # Initialize the dataset
    dataset = Dataset()

    # Initialize metadatablock
    citation = Citation()
    privacy = Privacy()

    #Fill with harvested information
    citation.title = 
    citation.add_keyword()
    citation.add_author()


    # Fill in privacy relevant fields
    privacy.personal_data = "no"

    # Add each metadatablock to the dataset
    dataset.add_metadatablock(citation)
    dataset.add_metadatablock(privacy)

    print(dataset)

    # Upload the dataset
    #p_id = dataset.upload (dataverse_name="roy_dataverse")
    #print('Dataset created and directory uploaded successfully.')

create_dataset()

