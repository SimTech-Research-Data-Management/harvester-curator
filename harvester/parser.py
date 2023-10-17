from lxml import etree
from typing import Optional
from sdRDM import DataModel
import os
import crawler
import vtk
import pyvista as pv

class Parser():
    """This class contains different parsers to parse files with various extensions.""" 

    
    def __init__(self):      
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
        

    def parse_xml(self, xml_file: str) -> dict:
        """
        This function parses an input xml file to extract metadata

        Args:
            xml_file (str): An input xml file
          
        Returns:
            meta_dict (dict): A dictionary that contains extracted metadata          
        """ 
      
        # Parse the XML file
        tree = etree.parse(xml_file)
        root = tree.getroot()


        # Create a dictionary to hold the metadata extracted from the file
        meta_dict = {}
      
        # Find and get the elements from the file and append them to metadata dictionary
        for title in root.xpath('//title'):
            title_ = title.get('title')
            year = title.find('year').text
          
            self.append_value(meta_dict, "title", title_)
            self.append_value(meta_dict, "year", year)
          
        for author in title.xpath('./author_name'):
            author = author.get('name')
            self.append_value(meta_dict, "author", author)
          
        return meta_dict
       
       
    def parse_txt(self, txt_file: str) -> dict:
        """
        This function parses an input txt file to extract metadata

        Args:
            txt_file (str): An input text file

        Returns:
            meta_dict (dict): A dictionary that contains extracted metadata  
        """  

        # Create a dictionary to hold the metadata extracted from the file
        meta_dict = {}
        
        # Read the author name(s) from the file and append to metadata dictionary
        with open(txt_file, "r") as file:
            for line in file:
                if "Author Name:" in line:
                    author = line.split("Author Name:")[1].strip()
                    self.append_value(meta_dict, "author", author)
        
        return meta_dict


    def parse_vtu(self, vtu_file:str) -> dict:
        """
        This function parses an input vtu file to extract metadata based on a markdown model of vtk specifications

        Args:
            vtu_file (str): An input vtu file
            
        Returns:
            meta_dict (dict): A dictionary that contains extracted metadata  
        """  

        # Create a dictionary to hold the metadata extracted from the file
        meta_dict = {}
        
        # Markdown model that contains contains vtk schema
        vtu_model = "vtu_model.md"
        vtu_model_filepath = os.path.join(os.getcwd(), os.path.join("specifications", vtu_model))
        
        # Read vtu model to generate the Python objects needed for parsing vtu files
        lib = DataModel.from_markdown(vtu_model_filepath)
        # Extract metadata from an input vtu file
        dataset = lib.VTKFile.from_xml(open(vtu_file))
        # Convert metadata output to a dict
        meta_dict = dataset.to_dict()
        # Remove the key "__source__" from meta dict 
        if "__source__" in meta_dict:
            del meta_dict["__source__"]
            
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
        else:
            output = pv.read(vtk_file)
        #print(f"file name: {os.path.basename(vtk_file)}")
        #print(f"meta properties extracted: \n{output}\n")

        # Get dataset type (geometry/topology) 
        dataset_type = str(type(output)).replace("'>", "").split(".")[-1]#
        self.append_value(meta_dict, "dataset type", dataset_type)           

        # Add extracted meta properties to meta_dict
        if dataset_type == "MultiBlock":            
            number_of_blocks = output.n_blocks
            self.append_value(meta_dict, "number of blocks", number_of_blocks)                  
        else:                  
            number_of_points = output.n_points
            number_of_cells = output.n_cells
            number_of_arrays = output.n_arrays
            
            self.append_value(meta_dict, "number of points", number_of_points)
            self.append_value(meta_dict, "number of cells", number_of_cells)   
            self.append_value(meta_dict, "number of arrays", number_of_arrays)

            array_names = {}
            # Extract array names if there exists dataset arrays
            if number_of_arrays:
                cell_data_array_names = output.cell_data.keys()
                if cell_data_array_names:
                    array_names["cell_data_array_name(s)"] = cell_data_array_names            
                point_data_array_names = output.point_data.keys()
                if point_data_array_names:
                    array_names["point_data_array_name(s)"] = point_data_array_names   
                field_data_array_names = output.field_data.keys()
                if field_data_array_names:
                    array_names["field_data_array_name(s)"] = field_data_array_names   
            
            self.append_value(meta_dict, "array names", array_names)
      
             
            if dataset_type == "ImageData":
                dimensions = output.dimensions
                spacing = output.spacing
                self.append_value(meta_dict, "dimensions", list(dimensions))
                self.append_value(meta_dict, "spacing", list(spacing))  
                
            elif dataset_type == "PolyData":           
                 number_of_lines = output.n_lines
                 self.append_value(meta_dict, "number of lines", number_of_lines)
                     
                 number_of_triangle_strips = output.n_strips
                 self.append_value(meta_dict, "number of triangle strips", number_of_triangle_strips)
                
            elif dataset_type in ("RectilinearGrid", "StructuredGrid"):
                dimensions = output.dimensions
                self.append_value(meta_dict, "dimensions", list(dimensions))
            else:
                pass
                                     
        mesh_bounds = output.bounds
        mesh_center = output.center
        
        self.append_value(meta_dict, "mesh bounds", list(mesh_bounds))
        self.append_value(meta_dict, "mesh center", list(mesh_center))    
        
        return meta_dict