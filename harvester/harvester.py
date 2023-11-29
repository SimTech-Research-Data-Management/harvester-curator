import os
from typing import Optional, Type
from crawler import crawler
from parser import Parser
from file_group import File, FileGroup, SuperGroup
import argparse


def harvester(path: str, verbose: Optional[bool] = False) -> Type[SuperGroup]:
    """
    This function harvests metadata from files under a given path by using parsers that parse files with different filetypes


    Args:
        path: Base directory for metadata harvesting
        verbose: A boolean indicating if messages should be generated regarding unparsed file(s) and filetype(s) in the given path


    Returns:
        all_file_groups: An instance of SuperGroup that contains all groups of files parsed for metadata and harvested metadata
    """
    if verbose:
        print(f"Start havesting metadata from files under the given path {args.path} ...\n")
  
    # Find all files under the given path
    file_dict = crawler(path)
    # Create an instance of Parser class
    parser = Parser()


    # Create a dictionary to hold the filetypes that has no corresponding parsers
    unparsed_file_type_dict = {}


    # Create an instance of SuperGroup class to hold all parsed files grouped based on file_types.
    all_file_groups = SuperGroup(name="all parsed file groups", file_group_names = {}, groups=[])

    # File formats (extensions) categorized into different groups
    VTK_FILE = ['vti', 'vtp', 'vtr', 'vts', 'vtu', 'vtk', 'pvti', 'pvtp', 'pvtr', 'pvts', 'pvtu', 'hdf', '.h5', '.hdf5'] 
    IMAGE_FILE_2D = ['jpg', 'jpeg', 'png', 'tif', 'tiff', 'pnm', 'pgm', 'ppm', 'img', 'bmp']
    IMAGE_FILE_3D = ['fib', 'ply', 'stl', 'obj', 'g','glb', 'exo', 'dcm', 'facet', 'slc', 'mhd', 'dem']
       
    # Use file parsers to extract metadata from files
    if file_dict:
        for file_type in file_dict:
            
            if file_type in VTK_FILE + IMAGE_FILE_2D + IMAGE_FILE_3D:
                file_type_parser_name = "parse_vtk"
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
                else:
                    file_group_name = file_type + " files"
                    
                # Create an instance of FileGroup for the specific file_type if not exists
                # and add it to SuperGroup instance's list of groups
                
                if file_group_name not in all_file_groups.file_group_names.keys():
                    all_file_groups.file_group_names[file_group_name] = [file_type]
                    globals()[file_group_name] = FileGroup(name=file_group_name, files=[])
                    all_file_groups.groups.append(globals()[file_group_name])            
                else:
                    all_file_groups.file_group_names[file_group_name].append(file_type)
                                  
                for file in file_dict[file_type]:
                    file_name = os.path.split(file)[1]
                    # Use parser to extract metadata from file
                    metadata = file_type_parser(file)
                    # Create an instance of File and append it to the corrsponding FileGroup's list of files
                    file_object = File(name=file_name, path=file, metadata=metadata)
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
            print(f"\n\n***Please note that currently there are no parsers to parse {', '.join(unparsed_file_types[:-1])} and {unparsed_file_types[-1]} files found under the given path.\n")
            print(f"List of unparsed files: {unparsed_files}\n\n")
      
    return all_file_groups

if __name__ == "__main__":

    arg_parser = argparse.ArgumentParser(description="Harvest metadata from files under a given path.")
    arg_parser.add_argument("--path", dest= "path", required=True, help="Base directory for metadata harvesting")
    arg_parser.add_argument("-v", "--verbose", action="store_true", help="Generate messages regarding unparsed file(s) and filetype(s)")

    args = arg_parser.parse_args()
  
    #print(f"----- Harvesting metadata from files under the given path {args.path} -----\n")
  
    all_file_groups = harvester(args.path, args.verbose)
  
    print("---*** Metadata Harvester Output ***---\n")
    # Determine the parent directory of the given path
    parent_directory = os.path.abspath(os.path.join(args.path, os.pardir))

    # Create the 'harvester_output' directory if it doesn't exist
    output_directory = os.path.join(parent_directory, 'harvester_output')
    os.makedirs(output_directory, exist_ok=True)

    # Construct the path for the output file in the 'output' directory
    output_file_path = os.path.join(output_directory, 'harvester_output.json')

    # Print the path to the output file
    print(f"Output will be written to: {output_file_path}")

    print(all_file_groups.yaml())
    #print(f"--- Tree visulization of metadata harvested---\n")
    #all_file_groups.visualize_tree()
    #print("\n")

    # Export output from metadata harvester into a JSON file
    with open(output_file_path, "w") as f:
        f.write(all_file_groups.json())