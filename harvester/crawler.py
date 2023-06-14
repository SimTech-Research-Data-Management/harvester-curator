import os
import magic

def crawler(path: str):
   """
   This function finds all files except the hidden ones in a directory and its subdirectories and groups the files by their type.
  
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
                # Use `file_magic.from_file` to get the file type
                file_type = file_magic.from_file(file_path)

                if file_type:
                    # Get the file extension from the MIME type
                    ext = file_type.split("/")[-1]
                else:
                    # Get the extension
                    print(f'Cannot guess file type! Collecting the extension of the file: {filename}.')
                    ext = os.path.splitext(filename)[1]

                # Add the file to the corresponding array in the dictionary
                if ext in file_dict:
                    file_dict[ext].append(file_path)
                else:
                    file_dict[ext] = [file_path]
            else:
                print(f"Not a file path: {file_path}")
   return file_dict
   

#if __name__ == '__main__':
#    print("----- A simple example of using crawler in a given directory ---- \n")
    
    # Define the target path that contains files
#    path = "/home/sarbani/darus_data_harvester/Example"
#    file_dict = crawler(path)
#    print(file_dict)