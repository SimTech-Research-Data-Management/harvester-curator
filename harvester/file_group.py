from sdRDM import DataModel, Field
from typing import List, Dict


class File(DataModel):
    name: str = Field(
        ...,
        description="Name of a file"
    )
  
    path: str = Field(
        ...,
        description="Path of a file"
    )
  
    metadata: Dict[str, object] = Field(
        ...,
        description="Metadata of the file"
    )


class FileGroup(DataModel):
    name: str = Field(
        ...,
        description="Name of the file group based on file type"
    )
  
    files: List[File] = Field(
        description="Files from this group",
        default_factory=list
    )


class SuperGroup(DataModel):
    name: str = Field(
        ...,
        description="Group of all file groups"
    )

    file_group_names: Dict[str, object] = Field(
        ...,
        description="List of the names of file groups"
    )
    
    groups: List[FileGroup] = Field(
        description="FileGroup from the super group",
        default_factory=list
    )

