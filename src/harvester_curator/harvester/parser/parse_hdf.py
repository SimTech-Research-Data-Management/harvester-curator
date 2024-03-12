import os
import h5py
from typing import Union, Any, Dict

def extract_hdf5_metadata(name: str, obj: Union[h5py.Group, h5py.Dataset], item_list: Dict[str, Any]) -> None:
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
            item_list[": ".join(["group_name", group_name])] = [{"group_metadata": group_attributes}]     
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
        if current_group_name_record in item_list:
            item_list[current_group_name_record].append({": ".join(["dataset_name", dataset_name]): {"dataset_metadata": dataset_all_metadata}})
        else:     
            item_list[current_group_name_record] = [{": ".join(["dataset_name", dataset_name]): {"dataset_metadata": dataset_all_metadata}}]
            
    else:
        print(f"item: {item_name} is neither group nor dataset")
    
    

def parse_hdf5(hdf5_file: str) -> dict:
    """
    This function parses an hdf5 file (.hdf5, .h5, .he5) to extract metadata

    Args:
        hdf5_file (str): An input hdf5 file
        
    Returns:
        meta_dict (dict): A dictionary that contains extracted metadata        
    """      
    item_list = {}
    with h5py.File(hdf5_file, "r") as f: 
        f.visititems(lambda name, obj: extract_hdf5_metadata(name, obj, item_list))
    meta_dict = item_list

    return meta_dict