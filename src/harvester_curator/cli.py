import typer

from typing_extensions import Annotated
from pathlib import Path

from harvester_curator.harvester.harvester import harvester
from harvester_curator.curator.curator import curator
from harvester_curator.curator.dataset_upload import dataset_upload

app = typer.Typer()


harvester_output_filename = "harvested_output.json"
curator_output_filename = "curated_output.json"
api_endpoints_filename = "darus_md_schema_api_endpoints.json"

base_dir = Path(__file__).parent
default_harvester_dir = base_dir / "example" / "use-case"
default_api_endpoints_path = base_dir / "curator" / "api_end_points" / api_endpoints_filename

project_root = Path(__file__).resolve().parents[2]
default_output_dir_name = "output"
default_harvester_output_path = project_root / default_output_dir_name / harvester_output_filename
default_curator_output_path = project_root / default_output_dir_name / curator_output_filename



@app.command()
def harvest(
    dir_path: Annotated[str, typer.Option(
        ...,
        "--dir_path",
        "-d",
        help="Path of the base directory from which metadata is harvested"
    )] = str(default_harvester_dir),
    output_filepath: Annotated[str, typer.Option(
        ...,
        "--output_filepath",
        "-o",
        help="Path of the JSON file to save harvested metadata"
    )] = str(default_harvester_output_path),
    verbose: Annotated[bool, typer.Option(
        ...,
        "--verbose",
        "-v",
        help="An boolean flag. If set to True, the function will provide messages about"
             "any unparsed files and file types encountered"
    )] = True
):
    """
    Harvest metadata from files within a specified directory and save the harvested metadata to a JSON file.

    Args:
        dir_path (str): Path of the base directory from which metadata is harvested.
        output_filepath (str): Path of the JSON file to save harvested metadata.
        verbose (bool): An boolean flag. If set to True, the function will provide messages about any unparsed
                    files and file types encountered. 
    """
    
    harvester(dir_path=dir_path, output_filepath=output_filepath, verbose=verbose) 


@app.command()
def curate(
    harvested_metadata_filepath: Annotated[str, typer.Option(
        ...,
        "--harvested_metadata_filepath",
        "-h",
        help="Path of the JSON file with harvested metadata"
    )] = str(default_harvester_output_path),
    output_filepath: Annotated[str, typer.Option(
        ...,
        "--output_filepath",
        "-o",
        help="Path of the JSON file to save curated metadata"
    )] = str(default_curator_output_path),
    api_endpoints_filepath: Annotated[str, typer.Option(
        ...,
        "--api_endpoints_filepath",
        "-a",
        help="Path of the JSON file with schema API endpoints for metadata blocks"
    )] = str(default_api_endpoints_path)
):
    """
    Compares harvested metadata against defined schemas from API endpoints, extracts matching metadata fields
    and their values, and transforms these fields to ensure their incoporability into the metadata blocks defined by the schemas.
    
    The function aligns the extracted metadata from various sources with the expected structure and data types 
    defined by the API schemas. This alignment facilitates accurate and efficient integration of metadata 
    into metadata blocks defined by schemaes from API endpoints, enhancing data consistency and interoperability.

    Args:
        harvested_metadata_filepath (str): The base directory from which metadata is harvested.
        output_filepath (str): Path of the JSON file to save curated metadata.
        api_endpoints_filepath (str): Path of the JSON file with schema API endpoints for metadata blocks
    """

    curator(harvester_output_filepath=harvested_metadata_filepath, 
            output_filepath=output_filepath, 
            api_endpoints_filepath=api_endpoints_filepath) 



@app.command()
def upload(
    server_url: Annotated[str, typer.Option(
        ...,
        "--server_url",
        "-s",
        help="Server address"
    )],
    api_token: Annotated[str, typer.Option(
        ...,
        "--api_token",
        "-a",
        help="API token for accessing Dataverse API"
    )],
    dataverse_id: Annotated[str, typer.Option(
        ...,
        "--dataverse_id",
        "-d",
        help="Alias of the host Dataverse for the dataset to be uploaded"
    )],
    curated_metadata_filepath: Annotated[str, typer.Option(
        ...,
        "--curated_metadata_filepath",
        "-c",
        help="Path of the JSON file that contains curated metadata "
    )] = str(default_curator_output_path)
):
    """
    Uploads a dataset with curated metadata to a given Dataverse installation 

    Args: 
        curated_metadata_filepath (str): Path of the JSON file that contains curated metadata 
        server_url (str): Server address
        api_token (str): API token for accessing Dataverse API
        dataverse_id (str): Alias of the host Dataverse for the dataset to be uploaded

    """
    
    dataset_upload(server_url=server_url, 
                   api_token=api_token,
                   dataverse_id=dataverse_id,
                   curated_metadata_filepath=curated_metadata_filepath)
 

def main():
    """Start the Typer app"""
    app()


if __name__ == "__main__":
    main()
