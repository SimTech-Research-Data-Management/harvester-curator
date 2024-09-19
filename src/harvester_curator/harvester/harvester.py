import os
import argparse
import json
import warnings
import numpy as np
import datetime
from typing import Type
from .crawler import crawler
from harvester_curator.harvester.parser.parser import Parser
from .file_group import File, FileGroup, SuperGroup
from pathlib import Path


# Filter out UserWarnings
warnings.filterwarnings("ignore", category=UserWarning)

class JsonSerialize(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        if isinstance(obj, np.dtype):
            return obj.descr
        if isinstance(obj, (datetime.datetime, datetime.date)):
            return obj.isoformat()
        return json.JSONEncoder.default(self, obj)


def harvest_metadata(dir_path: str, verbose: bool = False) -> Type[SuperGroup]:
    """
    This function harvests metadata from files located under a specified base directory. 
    It utilizes parsers tailored to different filetypes to extreact metadata. 


    Args:
        dir_path: The base directory path from which metadata is harvested.
        verbose: An optional boolean flag. If set to True, the function will provide messages about any unparsed
                 files and file types encountered. 


    Returns:
        all_file_groups: An instance of SuperGroup that contains all groups of files parsed for metadata and harvested metadata. 
    """
    if verbose:
        print(f"\nStart havesting metadata from files under the given base directory {dir_path} ...\n")
  
    # Find all files under the given path
    file_dict = crawler(dir_path)
    # Create an instance of Parser class
    parser = Parser()

    # Create a dictionary to hold the filetypes that has no corresponding parsers
    unparsed_file_type_dict = {}

    # Create an instance of SuperGroup class to hold all parsed files grouped based on file_types.
    all_file_groups = SuperGroup(supergroup_name="all parsed file groups", file_group_names={}, groups=[])

    # File formats (extensions) categorized into different groups
    VTK_FILE = ['vti', 'vtp', 'vtr', 'vts', 'vtu', 'vtk', 'pvti', 'pvtp', 'pvtr', 'pvts', 'pvtu', 'hdf'] 
    IMAGE_FILE_2D = ['jpg', 'jpeg', 'png', 'tif', 'tiff', 'dcm', 'pnm', 'pgm', 'ppm', 'img', 'bmp']
    IMAGE_FILE_3D = ['fib', 'ply', 'stl', 'obj', 'g','glb', 'exo', 'facet', 'slc', 'mhd', 'dem']
    HDF5_FILE = ["hdf5", "h5", "he5"]
       
    # Use file parsers to extract metadata from files
    if file_dict:
        for file_type in file_dict:
            
            if file_type in VTK_FILE + IMAGE_FILE_2D + IMAGE_FILE_3D:
                file_type_parser_name = "parse_vtk"
            elif file_type in HDF5_FILE:
                file_type_parser_name = "parse_hdf5" 
            else:
                file_type_parser_name = "parse_" + file_type

            # Check if parser exists for the specific file_type
            file_type_parser = getattr(parser, file_type_parser_name, None)
            # Use parser to parse the files of the specfic file_type if exists
            if file_type_parser:   
                if file_type in VTK_FILE: 
                    file_group_name = "vtk files"
                elif file_type in IMAGE_FILE_2D:
                    file_group_name = "2D image files"
                elif file_type in IMAGE_FILE_3D:
                    file_group_name = "3D image files"
                elif file_type in HDF5_FILE:
                    file_group_name = "hdf5 files"
                else:
                    file_group_name = file_type + " files"
                    
                # Create an instance of FileGroup for the specific file_type if not exists
                # and add it to SuperGroup instance's list of groups
                
                if file_group_name not in all_file_groups.file_group_names.keys():
                    all_file_groups.file_group_names[file_group_name] = [file_type]
                    globals()[file_group_name] = FileGroup(file_group_name=file_group_name, files=[])
                    all_file_groups.groups.append(globals()[file_group_name])            
                else:
                    all_file_groups.file_group_names[file_group_name].append(file_type)
                                  
                for file in file_dict[file_type]:
                    file_name = os.path.split(file)[1]
                    # Use parser to extract metadata from file
                    metadata = file_type_parser(file)
                    # Create an instance of File and append it to the corrsponding FileGroup's list of files
                    file_object = File(file_name=file_name, path=file, metadata=metadata)
                    globals()[file_group_name].files.append(file_object)
      
            else:
                unparsed_file_type_dict[file_type] = file_dict[file_type]          
    else:
        if verbose:
            print("No file is found under the given path\n")   


    # Print out information regarding unparsed file_types and files if verbose is True
    if unparsed_file_type_dict:
        unparsed_file_types = list(unparsed_file_type_dict.keys())
        unparsed_files = [file for sublist in unparsed_file_type_dict.values() for file in sublist]
        if verbose:
            print(f"***Please note that currently there are no parsers to parse {', '.join(unparsed_file_types[:-1])} and {unparsed_file_types[-1]} files found under the given path.\n")
            print(f"List of unparsed files: {unparsed_files}\n")

    return all_file_groups

def harvester(dir_path: str, output_filepath: str, verbose: bool = False) -> None:
    """
    This function harvests metadata from files within a specified directory and save the harvested metadata to a JSON file.


    Args:
        dir_path: The base directory from which metadata is harvested.
        output_filepath: Path of the JSON file to save harvested metadata.
        verbose: An boolean flag. If set to True, the function will provide messages about any unparsed
                 files and file types encountered. 

    """

    # Check if dir_path exists and is accessible
    dir_path_obj = Path(dir_path)
    if not dir_path_obj.exists() or not dir_path_obj.is_dir():
        raise FileNotFoundError(f"Invalid directory: The directory {dir_path} does not exist or is not accessible.")

    output_filepath_obj = Path(output_filepath)
    output_dir = output_filepath_obj.parent
    # Check if the parent directory of the output file exists
    if not output_dir.exists():
        try: 
            output_dir.mkdir(parents=True, exist_ok=True)
        except OSError as e:
            raise OSError(f"Output directory '{output_dir}' cannot be created. Error: {e}")

    # Check if the parent directory of the output file is a directory
    if not output_dir.is_dir():
        raise FileNotFoundError(f"Invalid directory: The output directory '{output_dir}' is not a directory.")

    # Check if the parent directory of the output file is writable
    if not os.access(output_dir, os.W_OK):
        raise PermissionError(f"Invalid directory: The output directory '{output_dir}' is not writable.")
    # Check if output_filepath has a .json extension
    if output_filepath_obj.suffix != ".json":
        raise ValueError("Invalid output filepath: The output filename must end with '.json'.")
    
    # Harvest metadata from the given base directory
    try: 
        harvested_metadata = harvest_metadata(dir_path, verbose)
        metadata_dict = harvested_metadata.dict()
    except Exception as e:
        raise RuntimeError(f"Error during metadata harvesting: {e}")

    # Create the output directory if it does not exists
    output_dir_path = Path(output_filepath).parent
    output_dir_name = output_dir_path.name
    try:
         output_dir_path.mkdir(parents=True, exist_ok=True)
    except OSError as e:
        print(f"Output directory {output_dir_name} cannot be created. Error: {e}")
            
    # Write harvested metadata to the specified output file
    try:
        with open(output_filepath, "w") as f:
            json.dump(metadata_dict, f, indent=2, allow_nan=True, cls=JsonSerialize)
            print(f"Harvested metadata successfully saved to {output_filepath}\n")
    except IOError as error:
        raise IOError(f"Failed to write to {output_filepath}")


# if __name__ == "__main__":

#     # arg_parser = argparse.ArgumentParser(description="Harvest metadata from files under a given path.")
#     # arg_parser.add_argument("--path", dest= "path", required=True, help="Base directory for metadata harvesting")
#     # arg_parser.add_argument("-v", "--verbose", action="store_true", help="Generate messages regarding unparsed file(s) and filetype(s)")

#     # args = arg_parser.parse_args()
  
#     # #print(f"----- Harvesting metadata from files under the given path {args.path} -----\n")
  
#     # all_file_groups = harvester(args.path, args.verbose)
  
#     # # print("---*** Metadata Harvester Output ***---\n")
#     # # Determine the parent directory of the given path
#     # parent_directory = os.path.abspath(os.path.join(args.path, os.pardir))

#     # # # Create the 'harvester_output' directory if it doesn't exist
#     # # output_directory = os.path.join(parent_directory, 'harvester_output')
#     # # os.makedirs(output_directory, exist_ok=True)

#     # # Construct the path for the output file in the 'output' directory
#     # output_file_path = os.path.join(parent_directory, 'harvester_output.json')

#     # # Export output from metadata harvester into a JSON file
#     # output_metadata = json.dumps(all_file_groups.dict(), indent=2, allow_nan=True, cls=JsonSerialize)
#     # with open(output_file_path, "w") as f:
#     #     f.write(output_metadata)
     
#     # # Print the path to the output file
#     # print(f"Output is written to: {output_file_path}")
#     dir_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "example", "use-case")
#     harvester(dir_path)