import os
import subprocess
import crawler
import vtk
import pyvista as pv
import h5py
import yaml
import json
import re
import numpy
from pyvista import examples
from typing import Union, Any, Dict
from utils import validate_json, get_json_from_url, validate_jsonld, remove_keys_with_prefix, format_author, process_authors, format_software_info

class Parser():
    """This class contains different parsers to parse files with various extensions.""" 

    
    def __init__(self) -> None:      
        pass

    def append_value(self, dict_: dict, key_: str, value_: str) -> dict:
        """
        This function appends a given value to a dictionary if it is not none.

        Args:
            dict_ (dict): A dictionary for appending a given value
            key_ (str): A string representing the key
            value_ (str): A sring value to be added

        Returns:
            dict_ (dict): A dictionary with appended value
        """
        if value_:
            if key_ in dict_:
                dict_[key_].append(value_)
            else:
                dict_[key_] = [value_]
      
        return dict_


    def extract_hdf5_metadata(self, name: str, obj: Union[h5py.Group, h5py.Dataset]) -> None:
        """
        Extract metadata from the first h5py Group or Dataset instance with the provided name
        
        Args:
            name: Name of h5py Group or Dataset
            obj: A h5py Group or Dataset

        Returns:
            None

        """
        item_name = obj.name
        if isinstance(obj, h5py.Group):
            group_name = item_name
            # Extract group metadata
            group_attributes = dict(list(obj.attrs.items()))
            if group_attributes:
                self.item_list[": ".join(["group_name", group_name])] = [{"group_metadata": group_attributes}]     
        elif isinstance(obj, h5py.Dataset):      
            dataset_all_metadata = []

            # Extract dataset metadata
            dataset_attributes = dict(list(obj.attrs.items()))      
            if dataset_attributes:
                dataset_all_metadata.append({"dataset_attributes": dataset_attributes})

            # Extract numpy attributes from dataset
            dataset_numpy_attributes = []
            dataset_type_string = str(type(obj.dtype)).split('.')[-1].replace("'>", "")
            dataset_type = "".join([dataset_type_string[-5:], "(", dataset_type_string[0:-5], ")"]).lower()
            dataset_numpy_attributes.append({"dataset_type": dataset_type})         
            dataset_numpy_attributes.append({"shape": obj.shape})
            dataset_numpy_attributes.append({"size": str(obj.size)})
            dataset_numpy_attributes.append({"ndim": obj.ndim})   
            dataset_numpy_attributes.append({"nbytes": obj.nbytes})     
            dataset_numpy_attributes.append({"maxshape": obj.maxshape})  
               
            if dataset_numpy_attributes:
                dataset_all_metadata.append({"dataset_numpy_attributes": dataset_numpy_attributes})             
                
            dataset_name = os.path.basename(item_name)
            current_group_name = os.path.dirname(item_name)
            current_group_name_record = ": ".join(["group_name", current_group_name])
            if current_group_name_record in self.item_list:
                self.item_list[current_group_name_record].append({": ".join(["dataset_name", dataset_name]): {"dataset_metadata": dataset_all_metadata}})
            else:     
                self.item_list[current_group_name_record] = [{": ".join(["dataset_name", dataset_name]): {"dataset_metadata": dataset_all_metadata}}]
                
        else:
            print(f"item: {item_name} is neither group nor dataset")
        
        
    
    def parse_hdf5(self, hdf5_file: str) -> dict:
        """
        This function parses an hdf5 file (.hdf5, .h5, .he5) to extract metadata

        Args:
            hdf5_file (str): An input hdf5 file
          
        Returns:
            meta_dict (dict): A dictionary that contains extracted metadata        
        """      
        self.item_list = {}
        with h5py.File(hdf5_file, "r") as f: 
            f.visititems(self.extract_hdf5_metadata)
        meta_dict = self.item_list

        return meta_dict
      
    def parse_vtk(self, vtk_file:str) -> dict:
        """
        This function parses an input vtk file to extract metadata 

        Args:
            vtk_file (str): An input vtk file
            
        Returns:
            meta_dict (dict): A dictionary that contains extracted metadata  
        """  
       
        # Create a dictionary to hold the metadata extracted from the file
        meta_dict = {}

        # Get file type of the input vtk file
        file_type = crawler.get_file_type(vtk_file)

        # Use Pyvista to read vtk file and get meta properties of vtk mesh     
        if file_type in ("pgm", "ppm"):
            reader = pv.PNMReader(vtk_file)
            output = reader.read()
        elif file_type in ("vtm", "vtmb"):
            reader = pv.XMLMultiBlockDataReader(vtk_file)
            output = reader.read()
            print(f"vtm reader output: {output}")
        # elif file_type in ("wrl", "vrml"):
        #     reader = vtk.vtkVRMLImporter()
        #     reader.SetFileName(vtk_file)
        #     output = reader.read()
        #     print(f"vrml reader output: {output}")   
        elif file_type == "pvtp":
            reader = vtk.vtkXMLPPolyDataReader()
            reader.SetFileName(vtk_file)
            reader.Update()
            output = pv.wrap(reader.GetOutput())  
        else:
            output = pv.read(vtk_file)
        #print(f"file name: {os.path.basename(vtk_file)}")
        #print(f"meta properties extracted: \n{output}\n")

        # Get dataset type (geometry/topology) 
        dataset_type = str(type(output)).replace("'>", "").split(".")[-1].replace("vtk", "")#
        self.append_value(meta_dict, "dataset_type", dataset_type) 
      

        # Add extracted meta properties to meta_dict
        if dataset_type == "MultiBlock":            
            number_of_blocks = output.n_blocks            
            self.append_value(meta_dict, "number_of_blocks", number_of_blocks)
            
        else:                  
            number_of_points = output.n_points
            number_of_cells = output.n_cells
            number_of_arrays = output.n_arrays
            
            self.append_value(meta_dict, "number_of_points", number_of_points)
            self.append_value(meta_dict, "number_of_cells", number_of_cells)   
            self.append_value(meta_dict, "number_of_arrays", number_of_arrays)

            array_names = {}
            # Extract array names if there exists dataset arrays
            if number_of_arrays:
                cell_data_array_names = output.cell_data.keys()
                if cell_data_array_names:
                    array_names["cell_data_array_names"] = cell_data_array_names            
                point_data_array_names = output.point_data.keys()
                if point_data_array_names:
                    array_names["point_data_array_names"] = point_data_array_names   
                field_data_array_names = output.field_data.keys()
                if field_data_array_names:
                    array_names["field_data_array_names"] = field_data_array_names   
            
            self.append_value(meta_dict, "array_names", array_names)
      
             
            if dataset_type == "ImageData":
                dimensions = output.dimensions
                spacing = output.spacing
                self.append_value(meta_dict, "dimensions", list(dimensions))
                self.append_value(meta_dict, "spacing", list(spacing)) 
                
            elif dataset_type == "PolyData":           
                 number_of_lines = output.n_lines
                 self.append_value(meta_dict, "number_of_lines", number_of_lines)
                     
                 number_of_triangle_strips = output.n_strips
                 self.append_value(meta_dict, "number_of_triangle_strips", number_of_triangle_strips)
                
            elif dataset_type in ("RectilinearGrid", "StructuredGrid"):
                dimensions = output.dimensions
                self.append_value(meta_dict, "dimensions", list(dimensions))
            else:
                pass
                                     
        mesh_bounds = output.bounds
        mesh_center = output.center
        
        self.append_value(meta_dict, "mesh_bounds", list(mesh_bounds))
        self.append_value(meta_dict, "mesh_center", list(mesh_center))   


        return meta_dict

    def parse_yaml(self, yaml_file: str) -> dict:
        """
        This function parses an yaml file to extract metadata

        Args:
            yaml_file (str): An input yaml file
          
        Returns:
            meta_dict (dict): A dictionary that contains extracted metadata        
        """      
        with open(yaml_file, 'r') as yaml_file:
            try:
                meta_dict = yaml.safe_load(yaml_file)
            except yaml.YAMLError as e:
                print(f"Error loading YAML: {e}")
                return {}

        return meta_dict

    def parse_cff(self, cff_file: str) -> dict:
        """
        This function parses a CFF file to extract metadata

        Args:
            cff_file (str): An input CFF file
          
        Returns:
            meta_dict (dict): A dictionary that contains extracted metadata        
        """      
        command = ["cffconvert", "--validate", "-i", f"{cff_file}"]
        try:
            # Execute the command
            #subprocess.run(command, check=True)
            subprocess.run(command, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            meta_dict = self.parse_yaml(cff_file)
            if 'type' in meta_dict:
                meta_dict['type_of_work'] = meta_dict['type']
                del meta_dict['type']

            for author in meta_dict['authors']:
                if 'orcid' in author:
                    author['authorIdentifierScheme'] = 'ORCID'

                    # get orcid_id from url and put it in meta_dict['authorIdentifier']
                    orcid_link = author['orcid']
                    if re.match(r'\d{4}-\d{4}-\d{4}-\d{3}[0-9X]', orcid_link):
                        author['authorIdentifier'] = orcid_link
                    else:
                        pattern = r'(?<=orcid.org/)\d{4}-\d{4}-\d{4}-\d{3}[0-9X]'
                        matches = re.findall(pattern, orcid_link)
                        if matches:
                            author['authorIdentifier'] = matches[0]
                    del author['orcid']
                        
        except subprocess.CalledProcessError as e:
            print(f"Error: {e}")
            return
        print(meta_dict)
        return meta_dict
    
    def parse_bib(self, bib_file: str) -> dict:
        """
        This function parses a BibTex file to extract metadata

        Args:
            bib_file (str): An input BibTex file
          
        Returns:
            meta_dict (dict): A dictionary that contains extracted metadata        
        """      
        meta_dict = {} 
        with open(bib_file, 'r') as file:

            try:
                bibtex_str = file.read()
                current_entry = {}

                lines = bibtex_str.split('\n')

                for line in lines:
                    line = line.strip()

                    if not line:
                        continue

                    if line.startswith('@'):
                        if current_entry:
                            # Convert the author string to a list of dictionaries
                            if 'author' in current_entry:
                                authors = current_entry['author'].split(' and ')
                                current_entry['author'] = [{'name': author.strip()} for author in authors]

                            # Add the current entry to meta_dict
                            for key, value in current_entry.items():
                                meta_dict.setdefault(key, value)
                                
                            current_entry = {}

                        entry_match = re.match(r'@(\w+){(.*),', line)
                        if entry_match:
                            entry_type, key = entry_match.groups()
                    else:
                        value_match = re.match(r'\s*([^=]*)\s*=\s*{(.*)},?', line)
                        if value_match:
                            key, value = value_match.groups()
                            current_entry[key.strip()] = value.strip()

                if current_entry:
                    # Convert the author string to a list of dictionaries
                    if 'author' in current_entry:
                        authors = current_entry['author'].split(' and ')
                        current_entry['author'] = [{'name': author.strip()} for author in authors]

                    # Add the current entry to meta_dict
                    for key, value in current_entry.items():
                        meta_dict.setdefault(key, value)
                        
            except subprocess.CalledProcessError as e:
                print(f"Error: {e}")
                return
            
            # print(meta_dict)

        return meta_dict

    def parse_json(self, json_file: str) -> dict:
        """
        This function parses a JSON file to extract metadata

        Args:
            json_file (str): Path to the input JSON file
          
        Returns:
            meta_dict (dict): A dictionary that contains extracted metadata        
        """ 
        valid_json_result = validate_json(json_file)
        if valid_json_result:
            filename = os.path.basename(json_file).lower()
            # Check if the JSON file is a codemeta file
            if "codemeta" in filename and "codemeta.jsonld" not in filename:
                codemeta_context_url = "https://raw.githubusercontent.com/codemeta/codemeta/master/codemeta.jsonld"
                codemeta_context = get_json_from_url(codemeta_context_url)
                if codemeta_context:
                    valid_jsonld_result = validate_jsonld(valid_json_result, codemeta_context)
                    if valid_jsonld_result:
                        filtered_codemeta_data = remove_keys_with_prefix(valid_json_result, "@", ["@id"])
                        # print(f"filtered_codemeta_data: {filtered_codemeta_data}")

                        author_keys_to_process = ["author", "contributor", "maintainer", "copyrightHolder"]
                        for key in author_keys_to_process:
                            value = filtered_codemeta_data.get(key, {})
                            if value: 
                                filtered_codemeta_data[key] = process_authors(value, key)

                        software_requirement_suggestions_indicators = ["Requirements", "Suggestions"]
                        for indicator in  software_requirement_suggestions_indicators: 
                            software_keys = ["software" + indicator, "software-" + indicator.lower(), "software_" + indicator.lower()]
                            software_infos = [filtered_codemeta_data.get(key, {}) for key in software_keys]
                            software_infos = list(filter(None, software_infos))

                            if software_infos:
                                software_infos = software_infos[0]
                                software_info_list = []
                                if isinstance(software_infos, dict):
                                    software_infos = software_infos.items()
                                for software_info in software_infos:    
                                    if isinstance(software_info, tuple):
                                        software_info = {software_info[0]:software_info[1]}
                                    software_info_list.append(format_software_info(software_info, indicator))

                                software_info_list = list(filter(None, software_info_list))
                                filtered_codemeta_data["".join(["software", indicator, "Item"])] = software_info_list
                                for key in software_keys: 
                                    filtered_codemeta_data.pop(key, None)
                        
                        # Check if development status is repo status url and then format it into valid input if ncessary
                        repostatus_url_pattern = re.compile(r'^https?://www\.repostatus\.org/#.+')
                        
                        DEVELPMENT_STATUS_INPUT = ["Concept", "WIP", "Active", "Inactive", "Unsupported", "Moved", "Suspended", "Abandoned"]

                        development_status = filtered_codemeta_data.get("developmentStatus")

                        if development_status and repostatus_url_pattern.match(development_status):
                            filtered_codemeta_data["developmentStatus"]= development_status.split("#")[-1].capitalize()
                    
                        if filtered_codemeta_data.get("developmentStatus") not in DEVELPMENT_STATUS_INPUT:
                            filtered_codemeta_data.pop("developmentStatus", None)
                        
                        meta_dict = filtered_codemeta_data
                    else:
                        print(f"Faild to validate {json_file} against JSONLD schema {codemeta_context_url}")
                        meta_dict = {}

                else:
                    print(f"Failed to fetch codemeta context from URL {codemeta_context_url}")
                    meta_dict = {}
            else:
                meta_dict = valid_json_result
        else:
            print("Failed to validate JSON file: {json_file}")  
            meta_dict = {}
      
        return meta_dict
