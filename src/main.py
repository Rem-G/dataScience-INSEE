import pandas as pd
import os
from pathlib import Path
import requests
import json
import zipfile
import argparse

from data import *
from statistic import *

def auth_api(url):
	token_auth = '0f045f2a33890a5e3b11911fff10efc9918c0785d7665299a8c8fa1d'

	headers={'Authorization': token_auth}
	response = requests.get(url, headers=headers)
	return response

def user_request():
	path_communes_fusion = str(Path(os.getcwd()).parent) + "/data/laposte_commnouv.csv"
	data_communes_fusion = pd.read_csv(path_communes_fusion, sep=';')
	df_communes_fusion = pd.DataFrame(data_communes_fusion, columns = ['Prise en compte', 'Code INSEE Commune Nouvelle', 'Code INSEE Commune Déléguée (non actif)'])

	old_communes = list()

	for old_commune in df_communes_fusion['Code INSEE Commune Déléguée (non actif)']:
		old_communes.append(old_commune)

	url = 'https://data.opendatasoft.com/api/records/1.0/search/?dataset=code-postal-code-insee-2015%40public&q={}'

	validation = False

	while not validation :
		request = input("Enter a city :\n")

		response = auth_api(url.format(request)).json()
		proposition = False
		user_validation = "n"

		try:
			if request.lower() not in response['records'][0]['fields']['nom_com'].lower():
				if 'ligne_5' in response['records'][0]['fields'].keys():
					print(response['records'][0]['fields']['code_postal'], response['records'][0]['fields']['ligne_5'], response['records'][0]['fields']['nom_reg'])
				else:
					print(response['records'][0]['fields']['code_postal'], response['records'][0]['fields']['nom_com'], response['records'][0]['fields']['nom_reg'])
			else:
				 print(response['records'][0]['fields']['code_postal'], response['records'][0]['fields']['nom_com'], response['records'][0]['fields']['nom_reg'])
			proposition = True
		except:
			proposition = False

		if proposition:
			user_validation = input("\nIs it the right place ? y/n\n")
		else:
			print("Any city found for ", request)

		if user_validation.lower() == 'y':
			validation = True
			ligne_5 = None
			insee_code = response['records'][0]['fields']['insee_com']
			nom_com = response['records'][0]['fields']['nom_com']
			dep_com = response['records'][0]['fields']['code_dept']
			population = response['records'][0]['fields']['population'] # Le [i] corresponds à la hierarchie des communes
																		# fusionnées. [0] correspondant à la commune
																		# principale
			if request.lower() not in response['records'][0]['fields']['nom_com'].lower():
				try:
					nom_com = response['records'][0]['fields']['ligne_5']
				except:
					pass

			if float(insee_code) in old_communes:
				print("\nData is available until ", df_communes_fusion['Prise en compte'][old_communes.index(float(insee_code))], "\n")

			if "arrondissement" in nom_com.lower():
				nom_split = nom_com.split("-")
				nom_com = " ".join(nom_split)

	print("INSEE code :\n", insee_code)
	print("Population :\n", population)
	print("Name :\n", nom_com)

	return [nom_com, dep_com]

def main(dbreset = False):
	data = Data()
	statistic = Statistic()

	if dbreset:
		print("###############")
		print("Reset databases")
		print("############### \n")

	if dbreset or not os.path.isfile(str(Path(os.getcwd()).parent) + "/data/population_1968-2016.db"):

		if not os.path.isfile(str(Path(os.getcwd()).parent) + "/data/pop-sexe-age-quinquennal6816.xls"):
			with zipfile.ZipFile(str(Path(os.getcwd()).parent) + "/data/pop-sexe-age-quinquennal6816.xls.zip", 'r') as zip_ref:
				zip_ref.extractall(str(Path(os.getcwd()).parent) + "/data")

		data.create_db(True, "pop-sexe-age-quinquennal6816.xls")
		data.add_columns(str(Path(os.getcwd()).parent) + "/data/population_1968-2016.db")

	if dbreset or not os.path.isfile(str(Path(os.getcwd()).parent) + "/data/population_social_categories_1968-2016.db"):

		if not os.path.isfile(str(Path(os.getcwd()).parent) + "/data/pop-socialcategories.xls"):
			with zipfile.ZipFile(str(Path(os.getcwd()).parent) + "/data/pop-socialcategories.xls.zip", 'r') as zip_ref:
				zip_ref.extractall(str(Path(os.getcwd()).parent) + "/data")

		data.create_db(False, "pop-socialcategories.xls")

	com_dep = user_request()
	population = data.read_db_population(str(Path(os.getcwd()).parent) + "/data/population_1968-2016.db", "2011", com_dep[0], com_dep[1])
	print(population, "POPULATION")

	year = int(input("\nChoose a year (1968/1975/1982/1990/1999/2006/2011/2016) :\n"))
	print("\nIn", year, "there was", statistic.pop_stats(year)[0], "women aged between 20 and 24 and", statistic.pop_stats(year)[1], "men aged between 20 and 24\n") # Ca prend toutes les communes, je n'ai pas réussi à choisir une commune en particulier

if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument("--dbreset", help="Reset databases", action="store_true")
	args = parser.parse_args()

	if args.dbreset:
		main(dbreset = True)
	else:
		main()




