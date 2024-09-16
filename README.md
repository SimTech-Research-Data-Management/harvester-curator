# harvester-curator

<!--![harvester-curator Basic Idea](images/harvester_curator.png)-->
<p align="left">
<img src="images/harvester_curator.png" width="600" height="250">
</p>

`harvester-curator` is a Python-based automation tool designed to streamline metadata collection and management in research data management. It automates the extraction of metadata from source repositories or directories, and then seamlessly maps and adapts this metadata to comply with the designated repository's metadata schemas, preparing it for integration into datasets.

In essence, `harvester-curator` synergizes file crawling and crosswalking capabilities to automate the complex and labor-intensive processes of metadata collection and repository population. Tailored for efficiency and accuracy in Dataverse environments, it equips researchers with a streamlined method to accelerate data management workflows, ensuring that their research data aligns with the FAIR principles of Findability, Accessibility, Interoperability, and Reusability.

## Tool Workflow 

`harvester-curator` simplifies metadata collection and integration into research data repositories through two primary phases: the `Harvester` phase, focusing on the automated extraction of metadata, and the `Curator` phase, dedicated to mapping and adapting this metadata for integrating into datasets within a target repository.
<!--![harvester-curator Workflow Overview](images/workflow.png)-->
<p align="left">
<img src="images/workflow.png" width="700" height="300">
</p>

<details>

<summary> Detailed Tool Workflow (click to expand) </summary>

<br>

Let's delve deeper into the operational details of `harvester-curator`'s workflow.

`harvester-curator` optimizes metadata collection and integration in two main phases:

<div style="padding-left: 35px;">

***Harvester Phase:** Automates the extraction of metadata from sources specified by the user, including repositories or directories.
<!--![harvester](images/harvester.png)-->

<img src="images/harvester.png" width="400" height="50" alt="harvester phase workflow diagram">

***Curator Phase:** Seamlessly maps and adapts the harvested metadata to ensure its integration into the target repository.
<!--![curator](images/curator.png)-->
<img src="images/curator.png" width="400" height="50" alt="curator phase workflow diagram">

</div>

### Harvester Phase

During the initial `Harvester` phase, a crawler methodically scans files within the source directory and its subdirectories, sorting them by type and extension. This results in files being systematically grouped for further processing. Customized parsers are then utilized to extract metadata from these categorized groups, compiling the data into a well-organized JSON format.

<!--![Crawerler to Parser](images/crawler_parser.png)-->
<img src="images/crawler_parser.png" width="600" height="200" alt="crawler_parser">

We currently support a variety of parsers, including VTK, HDF5, CFF, BibTeX, YAML and JSON: 

**VTK-parser:** Supports file types such as `vtk`, `vti`, `vtr`, `vtp`, `vts`, `vtu`, `pvti`, `pvtr`, `pvtp`, `pvts` and `pvtu`.

**HDF5-parser:** Handles formats including `hdf5`, `h5`, `he5`.

**JSON-parser:** Processes types `json` and `jsonld`.


### Curator Phase

In the subsequent `Curator` phase, `harvester-curator` aligns the harvested metadata with the metadata schemas of the target repository, such as DaRUS. It matches the harvested metadata attributes with those defined in the metadata schemas and integrates the values into the appropriate locations. Additionally, it supports direct upload of curated metadata to the destination repository. 

<!--![curator Algorithm](images/curator_algorithm.png)-->
<img src="images/curator_algorithm.png" width="800" height="400" alt="curator_algorithm">

The `Curator` algorithm employs mappings to reconcile discrepancies between the naming conventions of harvested metadata and the metadata schemas of the target repository. Given that harvested metadata typically features a flat structure -- where attributes, values, and paths are at the same level, unlike the hierarchical organization common in repository schemas—-the algorithm adapts harvested metadata to ensure compatibility:

1. **Mapping and Matching:** It begins by updating attribute values and paths of harvested metadata based on predefined mappings, taking into account the hierarchical structure of repository schemas.
2. **Attribute Matching:** The algorithm searches for matching attributes within the target repository's schema. If no direct match is found, it combines parent and attribute information in search of a suitable match. Attributes that remain unmatched are noted for subsequent matching attempts with an alternative schema. 
3. **Parent Matching:** Upon finding a match, the algorithm designates the corresponding parent from the schema as the "matching parent." If a direct parent match does not exist, or if multiple matches are found, it examines common elements between the schema and harvested metadata to determine the most appropriate matching parent.
4. **Dictionary Preparation:** Attributes that successfully match are compiled into a dictionary that includes the mapped attribute, value, parent, and schema name, ensuring the metadata is compatible with the target repository.
5. **Similarity Matching:** When exact matches are not found across all schemas, the algorithm employs similarity matching with an 85% threshold to accommodate differences in metadata schema integration.

This systematic approach ensures compatibility with the requirements of the target repository and enhances the precision of metadata integration by utilizing direct mapping, exact matching and similarity matching to overcome schema alignment challenges.

</details>

## Project Structure
The `harvester-curator` project is organized as follows:

* `src/harvester_curator/`: The main app package directory containing all the source code.
* `tests/`: Contains all tests for the `harvester-curator` application.
* `images/`: Contains images used in the documentation, such as the workflow diagram.


## How to Install harvester-curator:
`harvester-curator` can be seamlessly installed using one of two methods: either through the Poetry package manager, which offers advanced dependency management and automatic creation of virtual environment, or by leveraging the traditional "setup.py" script, which follows the conventional Python distribution approach. 
### Installing Using Poetry
Install "harvester-curator" via Poetry:
#### 1. Install and Configure Poetry: 
Install Poetry with the following command:
```bash
curl -sSL https://install.python-poetry.org | python3 -
```
Configure Poetry to create virtual environment in the project folder
```bash
poetry config virtualenvs.in-project true 
```
#### 2. Clone the Repository:
```bash
git clone https://github.com/SimTech-Research-Data-Management/harvester-curator.git
```
#### 3. Change directory to be harvester-curator
```bash
cd harvester-curator
```
#### 4. Install harvester-curator dependencies and activate virtual environment:
Install harvester-curator dependencies
```bash
poetry install --no-ansi
```
Activate virtual environment
```bash
poetry shell
```
This method creates a virtual environment and installs all necessary dependencies along with "harvester-curator".

### Installing Using setup.py
For those who prefer or require a traditional installation method using "setup.py":
#### 1. Clone the Repository:
```bash
git clone https://github.com/SimTech-Research-Data-Management/harvester-curator.git
```
#### 2. Change directory to be harvester-curator
```bash
cd harvester-curator
```
#### 3. Install harvester-curator:
```bash
python3 -m pip install .
```
## Usage 
The `harvester-curator` app is designed to facilitate the efficient collection, curation and uploading of metadata. Follow these instructions to utilize the app and its available subcommands effectively.

### General Help
For an overview of all commands and their options:
```bash
harvester-curator --help
```
### Harvesting Metadata
To collect metadata from files in a specified directory:
```bash
harvester-curator harvest --dir_path "/path/to/directory" --output_filepath "/path/to/harvested_output.json"
```
Or, using short options:
```bash
harvester-curator harvest -d "/path/to/directory" -o "/path/to/harvested_output.json"
```
**Important Note:** Without `--dir_path`, the default is the `example` folder within the `harvester_curator` package. Without `--output_filepath`, harvested metadata is saved to `output/harvested_output.json` by default.

### Curating Metadata
To process and align harvested curation with specified schema metadata blocks:
```bash
harvester-curator curate  --harvested_metadata_filepath "/path/to/harvested_output.json" --output_filepath "/path/to/curated_output.json" --api_endpoints_filepath "/path/to/schema_api_endpoints.json"
```
Or, using short options:
```bash
harvester-curator curate  -h "/path/to/harvested_output.json" -o "/path/to/curated_output.json" -a "/path/to/schema_api_endpoints.json"
```
**Important Note:** Default file paths are used if options are not specified:
* `--harvested_metadata_filepath` defaults to `output/harvested_output.json`.
* `--output_filepath` defaults to `output/curated_output.json`.
* `--api_endpoints_filepath` defaults to `curator/api_end_points/darus_md_schema_api_endpoints.json`.

### Uploading Metadata
To upload curated metadata to a Dataverse repository as dataset metadata:
```bash
harvester-curator upload  --server_url "https://xxx.xxx.xxx" --api_token "abc0_def123_gkg456__hijk789" --dataverse_id "mydataverse_alias" --curated_metadata_filepath "/path/to/curated_output.json"
```
Or, using short options:
```bash
harvester-curator upload  -s "https://xxx.xxx.xxx" -a "abc0_def123_gkg456__hijk789" -d "mydataverse_alias" -c "/path/to/curated_output.json"
```
**Important Note:** The default for `--curated_metadata_filepath` is `output/curated_output.json`.

## Install and Usage Example Using Google Colab:
Get started with `harvester-curator` by trying out our interactive notebooks in Google Colab. These examples will guide you through installing 
and using `harvester-curator` using two different methods: Poetry and setup.py. 

Golab Notebooks:
* Install and Usage Example Using Poetry: 
This notebook walks you through the process of installing `harvester-curator` using Poetry. Key topics include upgrading Python version, setting up a new Poetry environment, installing dependencies and basic usage of `harvester-curator`.  
    [Open in Colab](https://colab.research.google.com/drive/1HU4McyrCOOdg-KXtW4SVLnqjoyOl1-JV?usp=sharing)

* Install and Usage Example Using setup.py:
For those who prefer the traditional appraoch, this notebook details the steps to install `harvester-curator` using `setup.py`. It also covers upgrading Python version, installing dependenciesm and outlines basic usage of `harvester-curator`.  
    [Open in Colab](https://colab.research.google.com/drive/1P5niQyW9HC0ji-GgLLE3zaLBdxhTS7yy?usp=sharing)

<!--**Detailed documentation** https://docs.google.com/document/d/1-nOwCnVz_3FDLZ1XSMEO-h1dI1eTbXqqxKMkziwOfLM/edit-->
