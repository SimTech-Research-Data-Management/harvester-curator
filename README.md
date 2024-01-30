# Harvester-Curator
Harvester-Curator is a tool meticulously designed to streamline metadata collection and provisioning processes in research data management. Its primary goal is to automate the extraction of metadata from original repositories or directories containing code and data, seamlessly mapping and incorporating the collected metadata into destination research data repository hubs, with a specific focus on Dataverse installations.

The tool operates through two phases. In the initial 'harvester' phase, Harvester-Curator traverses files within user-owned repositories or directories, dynamically selecting parsers to extract metadata from various file formats, before consolidating the collected metadata into a coherent JSON format. Transitioning seamlessly into the second phase, Harvester-Curator assumes the role of a curator. It compares the harvested metadata with the metadata fields defined in the schema of the destination repository, such as DaRUS, and translates and incorporates the elements and values of the harvested metadata into the corresponding ones in the destination repository.

In essence, Harvester-Curator is a tool that combines file crawling and crosswalking capabilities to automate the often intricate and time-consuming process of metadata collection and repository population. Its design is rooted in enhancing efficiency and accuracy in research data management within Dataverse installations, providing researchers with a simple solution to expedite workflows and ensure the FAIRness of research data.

### How to Install and Run Harvester-Curator:
##### 1. Git clone repo:
<pre>
git clone https://github.com/SimTech-Research-Data-Management/Harvester-Curator.git
</pre>

##### 2. Change directory to be Harvester-Curator and pull the branch feature/example
<pre>
cd Harvester_Curator
git checkout feature/example
git pull origin feature/example
</pre>

##### 3. Install dependencies from [requirements.txt](https://github.com/SimTech-Research-Data-Management/Harvester-Curator/blob/feature/example/requirements.txt) using python 3.11 or python 3.12
<pre>
python3 -m pip install -r requirements.txt
</pre> 

##### 4. Run [harvester.py](https://github.com/SimTech-Research-Data-Management/Harvester-Curator/blob/feature/example/harvester/harvester.py) for metadata harvesting and [curator.py](https://github.com/SimTech-Research-Data-Management/Harvester-Curator/blob/feature/example/curator/curator.py) for metadata curating:

The harvester can take the path of user's directory as an input and outputs harvested metadata in a JSON file. An example folder can be found [here](https://github.com/SimTech-Research-Data-Management/Harvester-Curator/blob/feature/example/example/example_input_minimal). The meatadata from the user's directory can be harvested by executing
<pre>
python3 harvester/harvester.py --path /path/to/your/folder -v
</pre>
The harvested metadata has been output to the [harvester_output.json](https://github.com/SimTech-Research-Data-Management/Harvester-Curator/blob/feature/example/example/harvester_output.json) file within the example folder. One may follow the path shown at the end of the terminal output.

[curator.py](https://github.com/SimTech-Research-Data-Management/Harvester-Curator/blob/feature/example/curator/curator.py) is able to compare and match the harvested metadata, stored in the json file [harvester_output.json](https://github.com/SimTech-Research-Data-Management/Harvester-Curator/blob/feature/example/example/harvester_output.json), with the metadata schema from DaRUS or other Dataverse Installations. The matched metadata is then transformed into a format compatible with the corresponding metadata fields in DaRUS or other Dataverse installations, ensuring it can be used to populate the metadata fields.
<pre>
python3 curator/curator.py --darus --path /path/to/harvested_output.json
</pre>
The curated metadata has been output to the [md_com.json](https://github.com/SimTech-Research-Data-Management/Harvester-Curator/blob/feature/example/example/md_com.json) file within the example folder.

##### 5. Upload curated metadata to DaRUS or other Dataverse Installations by following the provided codes below.
**Important:** Prior to uploading to DaRUS or other Dataverse installations, please ensure the necessary environment variables are set up. Refer to the example below for guidance.
<pre>
export DATAVERSE_API_TOKEN=XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX >> ~/.bashrc
export DATAVERSE_URL=https://demodarus.izus.uni-stuttgart.de >> ~/.bashrc
</pre>
##### 5.1. Initialize a Dataset object
<pre>
from pyDaRUS import Dataset
dataset = Dataset()
</pre>
##### 5.2. Load the dataset with curated metadata
<pre>
dataset = Dataset.from_json(/path/to/md_com.json)
</pre>
##### 5.3. Upload the dataset
<pre>
dataset.upload(dataverse_name="my_dataverse")
dataset.update(contact_name="Jane Doe", contact_email="jane.doe@example.com")
</pre>

**Detailed documentation** https://docs.google.com/document/d/1-nOwCnVz_3FDLZ1XSMEO-h1dI1eTbXqqxKMkziwOfLM/edit
