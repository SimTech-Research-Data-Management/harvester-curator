# harvester-curator
`harvester-curator` is a tool meticulously designed to streamline metadata collection and provisioning processes in research data management. Its primary goal is to automate the extraction of metadata from original repositories or directories containing code and data, seamlessly mapping and incorporating the collected metadata into destination research data repository hubs, with a specific focus on Dataverse installations.

The tool operates through two phases. In the initial 'harvest' phase, `harvester-curator` traverses files within user-owned repositories or directories, dynamically selecting parsers to extract metadata from various file formats, before consolidating the collected metadata into a coherent JSON format. Transitioning seamlessly into the second phase, `harvester-curator` assumes the role of a curator. It compares the harvested metadata with the metadata fields defined in the schema of the destination repository, such as DaRUS, and translates and incorporates the elements and values of the harvested metadata into the corresponding ones in the destination repository. It also enables the upload of curated metadata to the destination repository. 

In essence, `harvester-curator` is a tool that combines file crawling and crosswalking capabilities to automate the often intricate and time-consuming process of metadata collection and repository population. Its design is rooted in enhancing efficiency and accuracy in research data management within Dataverse installations, providing researchers with a simple solution to expedite workflows and ensure the FAIRness of research data.

## Project Structure
The `harvester-curator` project is organized as follows:

* `src/harvester_curator/`: The main app package directory containing all the source code.
* `tests/`: Contains all tests for the `harvester-curator` application.
* `output/`: Default directory where harvested and curated metadata files are stored if no specific path is provided.


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
git clone https://github.com/SimTech-Research-Data-Management/Harvester-Curator.git
```
#### 3. Change directory to be Harvester-Curator and pull the branch package
```bash
cd Harvester-Curator
git checkout package
git pull origin package
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
git clone https://github.com/SimTech-Research-Data-Management/Harvester-Curator.git
```
#### 2. Change directory to be Harvester-Curator and pull the branch package
```bash
cd Harvester-Curator
git checkout package
git pull origin package
```
#### 3. Install harvester-curator:
```bash
python -m pip install .
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
Important Note: Without `--dir_path`, the default is the `example` folder within the `harvester_curator` package. Without `--output_filepath`, harvested metadata is saved to `output/harvested_output.json` by default.

### Curating Metadata
To process and align harvested curation with specified schema metadata blocks:
```bash
harvester-curator curate  --harvested_metadata_filepath "/path/to/harvested_output.json" --output_filepath "/path/to/curated_output.json" --api_endpoints_filepath "/path/to/schema_api_endpoints.json"
```
Or, using short options:
```bash
harvester-curator curate  -h "/path/to/harvested_output.json" -o "/path/to/curated_output.json" -a "/path/to/schema_api_endpoints.json"
```
Important Note: Default file paths are used if options are not specified:
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
Important Note: The default for `--curated_metadata_filepath` is `output/curated_output.json`.

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

**Detailed documentation** https://docs.google.com/document/d/1-nOwCnVz_3FDLZ1XSMEO-h1dI1eTbXqqxKMkziwOfLM/edit
