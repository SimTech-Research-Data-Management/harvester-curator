from pyDataverse.api import NativeApi
from pyDataverse.models import Dataset
from pyDataverse.utils import read_file

# Replace these values with your actual data
BASE_URL = "https://demodarus.izus.uni-stuttgart.de"
API_TOKEN = "a7a7e68e-2129-41b6-b6a4-b156cd3a120f"
DV_ALIAS = "roy_dataverse"

ds = Dataset()

# Specify the path to the JSON file
ds_filename = "dataset.json"
ds.from_json(read_file(ds_filename))

api = NativeApi(BASE_URL, API_TOKEN)
#print(ds.validate_json())
#print(ds.dsDescription)
#url = "{0}/dataverses/{1}/datasets".format(api)
resp = api.get_info_version()
#resp = api.create_dataset(DV_ALIAS, ds.json())
print(resp.json())