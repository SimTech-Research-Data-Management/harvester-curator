import os
from pyDaRUS import Citation, Dataset

def parseTXT(txtFile):
    """
    This Function parses an input txt file to extract metadata
    """

    # Read the author names from the file
    with open(txtFile, "r") as file:
        for line in file:
            if "Author Name:" in line:
                author_name = line.split("Author Name:")[1].strip()
                print(author_name)


    # Initialize Dataset
    dataset = Dataset()


    # Initialize metadatablocks you like to use
    citation = Citation()


    # Add author name to the citation metadata
    citation.add_author(name=author_name)


    # Add the citation metadatablock to the dataset
    dataset.add_metadatablock(citation)

    print(citation)