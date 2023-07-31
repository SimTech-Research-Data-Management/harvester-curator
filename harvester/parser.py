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

        # Create a new instance of vtkXMLFileReadTester for checking if the vtk file is in XML format
        vtk_XML_file_read_tester = vtk.vtkXMLFileReadTester()
        vtk_XML_file_read_tester.SetFileName(vtk_file)
        # TestReadFile returns 1 if the file is a VTK XML file, and 0 otherwise
        checker_result = vtk_XML_file_read_tester.TestReadFile()  

        """ 
           If vtk file is in XML format, get file datatype and file version
           and then use either python vtk reader (Solution1)
               or Jan's code to extract metadata based on file extension(Solution2)
               or use vtkXMLGenericDataObjectReader for all sorts of vtk XML files and extract extra info other 
                               than number of points and number of cells by using specific reader.(Solution3)
        """       
        if checker_result:
                                                                      
            file_version = vtk_XML_file_read_tester.GetFileVersion()
            dataset_type = vtk_XML_file_read_tester.GetFileDataType()

            # python vtk readers for reading vtk XML files based on file extension
            vtk_XML_reader_dict = {"vti": vtk.vtkXMLImageDataReader(),
                                   "vtr": vtk.vtkXMLRectilinearGridReader(),
                                   "vts": vtk.vtkXMLStructuredGridReader(),
                                   "vtp": vtk.vtkXMLPolyDataReader(), 
                                   "vtu": vtk.vtkXMLUnstructuredGridReader(), 
                                   "vtm": vtk.vtkXMLMultiBlockDataReader(), 
                                   "pvti": vtk.vtkXMLPImageDataReader(),
                                   "pvtr": vtk.vtkXMLPRectilinearGridReader(),
                                   "pvts": vtk.vtkXMLPStructuredGridReader(),
                                   "pvtp": vtk.vtkXMLPPolyDataReader(), 
                                   "pvtu": vtk.vtkXMLPUnstructuredGridReader()}

            vtk_XML_reader = vtk_XML_reader_dict[file_type]
            vtk_XML_reader.SetFileName(vtk_file)
            vtk_XML_reader.Update()
            
            output = vtk_XML_reader.GetOutput()
            number_of_points = output.GetNumberOfPoints()
            number_of_cells = output.GetNumberOfCells()

            
            self.append_value(meta_dict, "dataset type", dataset_type)           
            self.append_value(meta_dict, "number of points", number_of_points)
            self.append_value(meta_dict, "number of cells", number_of_cells)

            # for dataset yype of PolyData, extract extra metadata
            if dataset_type == "PolyData":
                number_of_verts = output.GetNumberOfVerts()
                number_of_lines = output.GetNumberOfLines()
                number_of_strips = output.GetNumberOfStrips()
                number_of_polys = output.GetNumberOfPolys()                
           
                self.append_value(meta_dict, "number of verts", number_of_verts)
                self.append_value(meta_dict, "number of lines", number_of_lines)
                self.append_value(meta_dict, "number of strips", number_of_strips)
                self.append_value(meta_dict, "number of polys", number_of_polys)
                
        else:
            
            # Existing vtk file readers from python for reading non-XML vtk files based on file extension
            vtk_reader_dict = {"vtk": vtk.vtkGenericDataObjectReader(),
                               "fib": vtk.vtkPolyDataReader(), 
                               "ply": vtk.vtkPLYReader(),                       
                               "stl": vtk.vtkSTLReader(),
                               "obj": vtk.vtkOBJReader(),
                               "g": vtk.vtkBYUReader()}
    
            vtk_polydata_extension = ["fib", "ply", "stl", "obj", "g"]
    
            # Read vtk files based on vtk file extensions and get output from readers
            reader = vtk_reader_dict[file_type]
                
            if reader is None:
                print(f"Currently there exitst no parser for vtk file: {file_type}")
            else:               
                reader.SetFileName(vtk_file)
                reader.Update()
    
                if file_type == "vtk":
                    
                    output_type = reader.ReadOutputType()
                    output_type_to_dataset_type = {0: "PolyData", 1: "StructuredPoints", 2: "StructuredGrid", 
                                                   3: "RectilinearGrid", 4: "UnstructuredGrid"}
                    dataset_type = output_type_to_dataset_type[output_type]
                    
                    output = reader.GetOutput()
                    number_of_points = output.GetNumberOfPoints()
                    number_of_cells = output.GetNumberOfCells()
                    
                    self.append_value(meta_dict, "dataset type", dataset_type)           
                    self.append_value(meta_dict, "number of points", number_of_points)
                    self.append_value(meta_dict, "number of cells", number_of_cells)
                    
                    if dataset_type == "PolyData":
                        #output = reader.GetPolyDataOutput()
                        # Extract points metadata 
                        point_output = output.GetPoints()
                        point_datatype = point_output.GetDataType()
                        
                         # Extract metadata for the Verts, Line, Strips and Polys elements#
                        number_of_verts = output.GetNumberOfVerts()
                        number_of_lines = output.GetNumberOfLines()
                        number_of_strips = output.GetNumberOfStrips()
                        number_of_polys = output.GetNumberOfPolys()
                                              
                        #self.append_value(meta_dict, "point datatype", point_datatype)
                        self.append_value(meta_dict, "number of verts", number_of_verts)
                        self.append_value(meta_dict, "number of lines", number_of_lines)
                        self.append_value(meta_dict, "number of strips", number_of_strips)
                        self.append_value(meta_dict, "number of polys", number_of_polys)                                                                                    
                else:
                    output = reader.GetOutput()
                    
                    if file_type == "ply":
                        number_of_vertices= output.GetNumberOfPoints()
                        number_of_faces = output.GetNumberOfCells()
                                       
                        self.append_value(meta_dict, "number of vertices", number_of_vertices)
                        self.append_value(meta_dict, "number of faces", number_of_faces)
        
                    elif file_type == "obj":
                        number_of_points = output.GetNumberOfPoints()
                        number_of_faces = output.GetNumberOfCells()
                        self.append_value(meta_dict, "number of points", number_of_points)
                        self.append_value(meta_dict, "number of faces", number_of_faces)
                        
                    else:
                        number_of_points = output.GetNumberOfPoints()
                        number_of_cells = output.GetNumberOfCells()
         
                        self.append_value(meta_dict, "number of points", reader.GetNumberOfPoints())
                        self.append_value(meta_dict, "number of cells", reader.GetNumberOfCells())
           
           
        return meta_dict