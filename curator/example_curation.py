from pyDaRUS import Dataset, Citation, Privacy
from pyDaRUS.metadatablocks.citation import SubjectEnum


def create_dataset():


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
create_dataset()
