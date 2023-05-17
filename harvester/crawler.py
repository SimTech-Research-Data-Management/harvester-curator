import os

# Define the directory path
root_dir_path = os.getcwd()

# Get the parent directory
parent_dir = os.path.dirname(root_dir_path)

# Create a dictionary to hold the file extensions and their corresponding file names
file_dict = {}

# Loop through all files and subdirectories in the specified directory
for root, dirs, files in os.walk(parent_dir):
    
    # exclude hidden directories and files
    dirs[:] = [d for d in dirs if not d.startswith('.')]
    files[:] = [file for file in files if not file.startswith('.')]

    # exclude the "harvester" directory
    if "harvester" in dirs:
        dirs.remove("harvester")
    
    for filename in files:
        
        # Get the extension of the file
        ext = os.path.splitext(filename)[1]
        
        # add the file to the corresponding array in the dictionary
        if ext in file_dict:
            file_dict[ext].append(os.path.join(root, filename))
        else:
            file_dict[ext] = [os.path.join(root, filename)]


# print the list of files by extension
for ext, files in file_dict.items():
    print(f"Files with extension '{ext}':")
    for file in files:
        print(file)
    print() # print a blank line to separate the lists
