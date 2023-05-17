import os
from parse.parse_txt import parseTXT
from parse.parse_xml import parseXML

# Define the directory path
root_dir_path = os.getcwd()

# Get the parent directory
parent_dir = os.path.dirname(root_dir_path)

# Create a dictionary to hold the file extensions and their corresponding file names
file_dict = {}

# A dict of available parsers for parsing files with various extensions.
parserDict = {"parseTXT": parseTXT, "parseXML": parseXML}

# Create a list to hold the extensions that has no corresponing parser
extensionList = []


# Loop through all files and subdirectories in the specified directory
for root, dirs, files in os.walk(parent_dir):
    
    # exclude hidden directories and files
    dirs[:] = [d for d in dirs if not d.startswith('.')]
    files[:] = [file for file in files if not file.startswith('.')]

    # exclude the "harvester" directory
    if "harvester" in dirs:
        dirs.remove("harvester")
    
    for filename in files:
        ext = os.path.splitext(filename)[1]
        file_path = os.path.join(root, filename)
    
        # Add the file to the corresponding array in the dictionary
        if ext in file_dict:
            file_dict[ext].append(file_path)
        else:
            file_dict[ext] = [file_path]
        
# Use file parsers to extract metadata from files
if file_dict:
    for extension in file_dict.keys():
        extensionParser = "parse" + extension[1:].upper()
        if extensionParser in parserDict:
            for file in file_dict[extension]:
                print(f"Extractions from {extension} files:\n")
                parserDict[extensionParser](file)
                print()
        else:
            extensionList.append(extension)
else:
    print("No file is found in the current directory and its subdirectories")


# print the list of files by extension
for ext, files in file_dict.items():
    print(f"Files with extension '{ext}':")
    for file in files:
        print(file)
    print() # print a blank line to separate the lists
