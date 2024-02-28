from pydantic import BaseModel, Field
from typing import List, Dict, Optional



class File(BaseModel):
    file_name: str = Field(
        ...,
        description="Name of a file"
    )
  
    path: str = Field(
        ...,
        description="Path of a file"
    )
  
    metadata: Optional[Dict[str, object]] = Field(
        ...,
        description="Metadata of the file"
    )
    

class FileGroup(BaseModel):
    file_group_name: str = Field(
        ...,
        description="Name of the file group based on file type"
    )
  
    files: List[File] = Field(
        description="Files from this group",
        default_factory=list
    )


class SuperGroup(BaseModel):
    supergroup_name: str = Field(
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

