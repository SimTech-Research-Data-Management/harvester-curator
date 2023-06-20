from lxml import etree
from typing import Optional
from sdRDM import DataModel
import os
import crawler
import vtk

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

        # Existing vtk file readers from python for reading vtk files based on file extension
        vtk_reader_dict = {"vti": vtk.vtkXMLImageDataReader(),
                           "vtp": vtk.vtkXMLPolyDataReader(), 
                           "vtr": vtk.vtkXMLRecitilinearGrid(),
                           "vts": vtk.vtkXMLStructuredGrid(),
                           "vtu": vtk.vtkXMLUnstructuredGridReader(),
                           "vtk": vtk.vtkXMLPolyDataReader(),            
                           "fib": vtk.vtkPolyDataReader(), 
                           "ply": vtk.vtkPLYReader(),
                           "vtm": vtk.vtkXMLMultiBlockDataReader(), 
                           "stl": vtk.vtkSTLReader(),
                           "obj": vtk.vtkOBJReader(),
                           "g": vtk.vtkBYUReader(),
                           "pvti": vtk.vtkXMLImageDataReader(),
                           "pvtp": vtk.vtkXMLPolyDataReader(), 
                           "pvtr": vtk.vtkXMLRecitilinearGrid(),
                           "pvts": vtk.vtkXMLStructuredGrid(),
                           "pvtu": vtk.vtkXMLUnstructuredGridReader()}

       vtk_polydata_extension = ["vtp", "vtk", "fib", "ply", "stl", "obj", "g", "pvtp"]
       if file_type in vtk_reader_dict:
           reader = vtk_reader_dict[file_type]
           output = reader.GetOutPut()
           print(f"output from vtk reader: \n\n {output}\n\n\n")
           vtk_datatype = str(type(output)).split(".")[-1].split("'")[0].lstrip("vtk")
           self.append_value(meta_dict, "datatype", vtk_datatype)
           
           
       else:
           raise file_type + "is not supported by vtk parser"
            
        return meta_dict