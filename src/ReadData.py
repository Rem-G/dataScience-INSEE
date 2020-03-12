import pandas as pd
import os
from pathlib import Path
import requests

path = str(Path(os.getcwd()).parent) + "/data/correspondances-code-insee-code-postal.csv"

df = pd.read_csv(path, sep=';')


token_auth = "52d08d9b-414d-3dc2-86b7-b38bc61c1066"

def auth_api(url):

	headers = { 'Authorization' : 'Token ' + token_auth }
	response = requests.get(url, headers=headers)
	return response

url = "https://api.insee.fr/metadonnees/nomenclatures/v1/geo/region/62176"

#curl -k -L -H 'Authorization: Bearer ACCESS_TOKEN 52d08d9b-414d-3dc2-86b7-b38bc61c1066' "https://api.insee.fr/metadonnees/nomenclatures/v1/geo/region/62176"


r = auth_api(url)
print(r)

#print(df.head(5))