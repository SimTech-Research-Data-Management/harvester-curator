import xml.etree.ElementTree as ET
from pyDaRUS import Citation, Dataset

# parse the XML file
tree = ET.parse('author_name.xml')
root = tree.getroot()

# find and get the elements
for title in root.iter('title'):
    Title = title.get('title')
    year = title.find('year').text
    for author in title.iter('author_name'):
        name = author.get('name')

# Initialize Dataset
dataset = Dataset()

# Initialize metadatablocks you like to use
citation = Citation()

# Add author name to the citation metadata
citation.add_author(name=name)
citation.title = Title
citation.add_description(date=year)

# Add the citation metadatablock to the dataset
dataset.add_metadatablock(citation)

print(citation.author, citation.title, citation.description)