import os
import magic
import argparse
from generate_codemeta import codemeta_from_install, codemeta_from_requirements, write_codemeta


def crawler(path: str) -> dict:
    """
    This function finds all files except the hidden ones in a directory and its subdirectories and groups the files by file type.
  
    Args:
        path: Base directory to find files
      
    Returns:
        file_dict: A dictionary where each key is a file type, and its associated value is a list of all files with the corresponding type.         
    """
  
    # Create a dictionary to hold the file extensions and their corresponding file names
    file_dict = {}
  
    # Get the list of files in the first level of the directory
    files_in_first_level = [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]

    # Check if any file in the first level contains "codemeta" in its name
    codemeta_files = [f for f in files_in_first_level if "codemeta" in f.lower()]

    codemeta_install = []
    codemeta_requirements = []

    if not codemeta_files:
    
        # Check if install.py is in the first level
        install_py_path = os.path.join(path, "install.py")
        if os.path.isfile(install_py_path):
            codemeta_install = codemeta_from_install(install_py_path)

        requirements_path = os.path.join(path, "requirements.txt")
        if os.path.isfile(requirements_path):
            codemeta_requirements = codemeta_from_requirements(requirements_path)

        write_codemeta(codemeta_install, codemeta_requirements, path)
    
    # Create a `magic.Magic` instance
    file_magic = magic.Magic(mime=True)

    # Loop through all files and subdirectories under the given path
    for root, dirs, files in os.walk(path):
      
        # Exclude hidden directories and files
        dirs[:] = [d for d in dirs if not d.startswith(".")]
        files[:] = [file for file in files if not file.startswith(".")]
  
        for filename in files:
      
            # Construct the file path
            file_path = os.path.join(root, filename)
            
            # Check if the path is a file
            if os.path.isfile(file_path):
                # Use `get_file_type` function to get the file type
                file_type = get_file_type(file_path)

                # Add the file to the corresponding array in the dictionary
                if file_type in file_dict:
                    file_dict[file_type].append(file_path)
                else:
                    file_dict[file_type] = [file_path]

            else:
                print(f"Not a file path: {file_path}")
                
    file_dict = dict(sorted(file_dict.items(), key=lambda x: x[0]))
    return file_dict
   
def get_file_type(file_path):
    extension = os.path.splitext(file_path)[1]
    file_type = extension.lower().lstrip('.')

    if not file_type:
        file_magic = magic.Magic(mime=True)
        file_type_ = file_magic.from_file(file_path)

        if file_type_:
            # Get the file extension from the MIME type
            ext = file_type_.split("/")[-1]
        else:
            # No MIME type or extension available
            ext = ""

        return ext
    else:
        return file_type


if __name__ == '__main__':
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Find files in a directory and its subdirectories.")
    parser.add_argument('--path', type=str, help='Target path to search for files.')
    args = parser.parse_args()

    if args.path:
        target_path = args.path
        file_dict = crawler(target_path)
        print(f"All files found by crawler in the directory: \n {file_dict}")
    else:
        print("Please provide a valid --path argument.")