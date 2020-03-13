import pandas as pd
import os
from pathlib import Path
import json
import requests

path_communes_fusion = str(Path(os.getcwd()).parent) + "/data/laposte_commnouv.csv"
data_communes_fusion = pd.read_csv(path_communes_fusion, sep=';')
df_communes_fusion = pd.DataFrame(data_communes_fusion, columns = ['Prise en compte', 'Code INSEE Commune Nouvelle', 'Code INSEE Commune Déléguée (non actif)'])

old_communes = list()

for old_commune in df_communes_fusion['Code INSEE Commune Déléguée (non actif)']:
	old_communes.append(old_commune)

token_auth = '0f045f2a33890a5e3b11911fff10efc9918c0785d7665299a8c8fa1d'

def auth_api(url):
	headers={'Authorization': token_auth}
	response = requests.get(url, headers=headers)
	return response

url = 'https://data.opendatasoft.com/api/records/1.0/search/?dataset=code-postal-code-insee-2015%40public&q={}'

validation = False

while not validation :
	request = input("Enter a city :\n")

	response = auth_api(url.format(request)).json()

	print(response['records'][0]['fields']['code_postal'], response['records'][0]['fields']['nom_com'], response['records'][0]['fields']['nom_reg'])

	user_validation = input("\nIs it the right place ? y/n\n")

	if user_validation.lower() == 'y':
		validation = True
		insee_code = response['records'][0]['fields']['insee_com']
		nom = response['records'][0]['fields']['nom_com']
		population = response['records'][0]['fields']['population'] # Le [i] corresponds à la hierarchie des communes
																	# fusionnées. [0] correspondant à la commune
																	# principale

		if float(insee_code) in old_communes:
			print("\nData is available until ", df_communes_fusion['Prise en compte'][old_communes.index(float(insee_code))], "\n")

print("INSEE code :\n", insee_code)
print("Population :\n", population)
print("Name :\n", nom)