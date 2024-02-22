import os
import magic

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


# if __name__ == '__main__':
#     print("----- A simple example of using crawler in a given directory ---- \n")
    
#     # Define the target path that contains files
#     target_path = os.path.join(os.path.dirname(os.getcwd()), "example")
    
#     file_dict = crawler(target_path)
#     print(f"All files found by crawler in the directory: \n {file_dict}")
