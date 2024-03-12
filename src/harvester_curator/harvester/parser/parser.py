from .append_value import append_value
from .parse_hdf import parse_hdf5
from .parse_vtk import parse_vtk
from .parse_yaml import parse_yaml
from .parse_cff import parse_cff
from .parse_bib import parse_bib
from .parse_json import parse_json

class Parser:
    """This class contains different parsers to parse files with various extensions."""
    
    def __init__(self) -> None:
        pass

    # Define methods to call parser functions
    def append_value(self, dict_: dict, key_: str, value_: str) -> dict:
        return append_value(dict_, key_, value_)

    def parse_hdf5(self, hdf5_file: str) -> dict:
        return parse_hdf5(hdf5_file)

    def parse_vtk(self, vtk_file:str) -> dict:
        return parse_vtk(vtk_file)

    def parse_yaml(self, yaml_file: str) -> dict:
        return parse_yaml(yaml_file)

    def parse_cff(self, cff_file: str) -> dict:
        return parse_cff(cff_file)

    def parse_bib(self, bib_file: str) -> dict:
        return parse_bib(bib_file)

    def parse_json(self, json_file: str) -> dict:
        return parse_json(json_file)
