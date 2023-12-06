# darus_data_harvester examples:

This project has two phases: harvesting and curating.

The harvester can take the path of user's directory as an input and outputs harvested metadata in a JSON file. An example folder can be found [here](https://github.com/SimTech-Research-Data-Management/darus_data_harvester/tree/feature/example/example/harvester_related/example_input_minimal). The meatadata from the user's directory can be harvested by executing
<pre>
python3 harvester.py --path /path/to/your/folder
</pre>
from the *harvester* folder. 

Then the harvested metadata can be accessed through *harvester_output.json*.One may follow the path shown at the end of the terminal output.

[test_curation.py](https://github.com/SimTech-Research-Data-Management/darus_data_harvester/blob/master/curator/curator.py) is able to create a dataset in demoDaRUS (a test system of DaRUS) from the metadata provided in the json file [test_metadata_example.json](https://github.com/SimTech-Research-Data-Management/darus_data_harvester/blob/feature/example/example/curator_related/harvested_metadata_example.json). 

- For curation, one first needs to add environment varibles as:

<pre>
export DATAVERSE_API_TOKEN=XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX >> ~/.bashrc
export DATAVERSE_URL=https://demodarus.izus.uni-stuttgart.de >> ~/.bashrc
</pre>

- then execute 
<pre>
python3 curator.py --darus --path /path/to/harvested_metadata.json
</pre>

- or, for the interactive version, execute
<pre>
python3 curator.py --darus -i --path /path/to/harvested_metadata.json
</pre>
from the *curator* folder. 

The feature interactive-curation checks similarity percentage between the metadata fields defined by the user and target repository (only DaRUS currently). If it is more than a threshold value (85% currently) then will interact with user to add metadata to the corresponding field in the target repository.

**Detailed documentation** https://docs.google.com/document/d/1-nOwCnVz_3FDLZ1XSMEO-h1dI1eTbXqqxKMkziwOfLM/edit