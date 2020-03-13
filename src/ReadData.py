import pandas as pd
import os
from pathlib import Path
import math

path_communes = str(Path(os.getcwd()).parent) + "/data/laposte_hexasmal.csv"
data_communes = pd.read_csv(path_communes, sep=';')
df_communes = pd.DataFrame(data_communes, columns = ['Code_commune_INSEE', 'Ligne_5', 'Nom_commune', 'Code_postal'])

path_communes_fusion = str(Path(os.getcwd()).parent) + "/data/laposte_commnouv.csv"
data_communes_fusion = pd.read_csv(path_communes_fusion, sep=';')
df_communes_fusion = pd.DataFrame(data_communes_fusion, columns = ['Prise en compte', 'Code INSEE Commune Nouvelle', 'Nom Commune Nouvelle Siège', 'Code INSEE Commune Déléguée (non actif)', 'Nom Commune Déléguée', 'Adresse 2016 - Ligne 5 Commune déléguée', 'Adresse 2016 - Ligne 6 Commune déléguée'])

communes = list()
old_communes = list()

for commune in df_communes['Nom_commune']:
	communes.append(commune)

for old_commune in df_communes_fusion['Adresse 2016 - Ligne 5 Commune déléguée']:
	old_communes.append(old_commune)

def search_commune(request):
	potential_communes = list()

	for commune in communes:
		if request.upper() in commune:
			index = communes.index(commune)

			if isinstance(df_communes['Ligne_5'][index], str):#not empty cell
				old_communes = search_old_commune(request)

				if len(old_communes):
					potential_communes += old_communes
				else:
					data = {
							"Nom commune" : df_communes['Ligne_5'][index],
							"Code postal" : df_communes['Code_postal'][index],
							"Code INSEE" : df_communes['Code_commune_INSEE'][index]
							}
			else:
				data = {
						"Nom commune" : df_communes['Nom_commune'][index],
						"Code postal" : df_communes['Code_postal'][index],
						"Code INSEE" : df_communes['Code_commune_INSEE'][index]
						}

			potential_communes.append(data)
			#communes.pop(index)

	return potential_communes


def search_old_commune(request):
	potential_communes = list()

	for old_commune in old_communes:
		if isinstance(old_commune, str) and request.upper() in old_commune:
			index = old_communes.index(old_commune)

			data = {
					"Nom commune" : old_communes[index],
					"Code INSEE" : df_communes_fusion['Code INSEE Commune Déléguée (non actif)'][index],
					"Données disponibles jusque" : df_communes_fusion['Prise en compte'][index]
					}
			potential_communes.append(data)
			old_communes.pop(index)

	return potential_communes


request = str(input("Enter a city :\n"))
potential_communes = search_commune(request)

for potential_commune in potential_communes:
	print(potential_commune)
