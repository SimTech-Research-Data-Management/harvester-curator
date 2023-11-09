# darus_data_harvester examples:

This project has two phases: harvesting and curating.

The harvester can take the path of user's repository as an input and outputs harvested metadata in a JSON file. Now, the repository path is fixed to [example](https://github.com/SimTech-Research-Data-Management/darus_data_harvester/tree/master/example). An interested user may replace _example_ folder with their own repository after cloning this reposirory.

Then meatadata can be harvested from user's repo by executing
```python3 harvester.py```

Then the harvested metadata can be accessed through *harvester_output.json*

**Please note that, currently, we are only limited to a *vtk-parser*, which can harvest from a small number of filetypes, as: "glb", "jpg", "obj", "pgm", "ply", "png", "pnm", "ppm", "pvti", "pvtp", "pvtr", "pvtu", "stl", "tif", "vti", "vtk", "vtp", "vtr", "vts", "vtu"**

Codes for the curation phase can be found at [feature/curation](https://github.com/SimTech-Research-Data-Management/darus_data_harvester/tree/feature/curation) branch. [test_curation.py](https://github.com/SimTech-Research-Data-Management/darus_data_harvester/blob/feature/curation/curator/test_curation.py) is able to create a dataset in demoDaRUS (a test system of DaRUS) from the metadata in the json file [test_metadata_example.json](https://github.com/SimTech-Research-Data-Management/darus_data_harvester/blob/feature/curation/curator/test_metadata_example.json). After the testing_phase, *test_metadata_example.json* will be replaced by *harvester_output.json*. 

For the curation, one needs to  execute 
```python3 test_curation.py```
from the *curator* folder. 

The feature for interactive curation is added in [feature/interactive_curation](https://github.com/SimTech-Research-Data-Management/darus_data_harvester/tree/feature/interactive_curation) branch. It checks similarity percentage between the metadata fields defined by the user and target repository (only DaRUS currently). If it is more than a threshold value (85% currently) then will interact with user to add metadata to the corresponding field in the target repository.

**Detailed documentation** https://docs.google.com/document/d/1-nOwCnVz_3FDLZ1XSMEO-h1dI1eTbXqqxKMkziwOfLM/edit
