import vtk
import pyvista as pv
from harvester_curator.harvester.parser.append_value import append_value
from harvester_curator.harvester.crawler import get_file_type

def parse_vtk(vtk_file:str) -> dict:
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
    file_type = get_file_type(vtk_file)

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
    append_value(meta_dict, "dataset_type", dataset_type) 
    

    # Add extracted meta properties to meta_dict
    if dataset_type == "MultiBlock":            
        number_of_blocks = output.n_blocks            
        append_value(meta_dict, "number_of_blocks", number_of_blocks)
        
    else:                  
        number_of_points = output.n_points
        number_of_cells = output.n_cells
        number_of_arrays = output.n_arrays
        
        append_value(meta_dict, "number_of_points", number_of_points)
        append_value(meta_dict, "number_of_cells", number_of_cells)   
        append_value(meta_dict, "number_of_arrays", number_of_arrays)

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
        
        append_value(meta_dict, "array_names", array_names)
    
            
        if dataset_type == "ImageData":
            dimensions = output.dimensions
            spacing = output.spacing
            append_value(meta_dict, "dimensions", list(dimensions))
            append_value(meta_dict, "spacing", list(spacing)) 
            
        elif dataset_type == "PolyData":           
                number_of_lines = output.n_lines
                append_value(meta_dict, "number_of_lines", number_of_lines)
                    
                number_of_triangle_strips = output.n_strips
                append_value(meta_dict, "number_of_triangle_strips", number_of_triangle_strips)
            
        elif dataset_type in ("RectilinearGrid", "StructuredGrid"):
            dimensions = output.dimensions
            append_value(meta_dict, "dimensions", list(dimensions))
        else:
            pass
                                    
    mesh_bounds = output.bounds
    mesh_center = output.center
    
    append_value(meta_dict, "mesh_bounds", list(mesh_bounds))
    append_value(meta_dict, "mesh_center", list(mesh_center))   


    return meta_dict