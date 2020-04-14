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
	parent_dir = Path(os.getcwd()).parent
	path_communes_fusion = Path.joinpath(parent_dir, "data", "laposte_commnouv.csv")
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
	parent_dir = Path(os.getcwd()).parent

	if dbreset:
		print("###############")
		print("Reset databases")
		print("############### \n")

		print("This operation may take a while\n")
		if input("Reset databases ? y/n : ").lower() == "n":
			dbreset = False

	if dbreset or not Path.joinpath(parent_dir, "data", "population_1968-2016.db").is_file():
		if not Path.joinpath(parent_dir, "data", "pop-sexe-age-quinquennal6816.xls").is_file():
			with zipfile.ZipFile(Path.joinpath(parent_dir, "data", "pop-sexe-age-quinquennal6816.xls.zip"), 'r') as zip_ref:
				zip_ref.extractall(Path.joinpath(parent_dir, "data"))

		data.create_db(True, "pop-sexe-age-quinquennal6816.xls")
		#data.add_columns(parent_dir + "/data/population_1968-2016.db")

	if dbreset or not Path.joinpath(parent_dir, "data", "population_social_categories_1968-2016.db").is_file():
		if not Path.joinpath(parent_dir, "data", "pop-socialcategories.xls").is_file():
			with zipfile.ZipFile(Path.joinpath(parent_dir, "data", "pop-socialcategories.xls.zip"), 'r') as zip_ref:
				zip_ref.extractall(Path.joinpath(parent_dir, "data"))

		data.create_db(False, "pop-socialcategories.xls")

	com_dep = user_request()
	population = data.read_db_population(parent_dir + "/data/population_1968-2016.db", "2011", com_dep[0], com_dep[1])
	print(population, "POPULATION")

	year = int(input("\nChoose a year (1968/1975/1982/1990/1999/2006/2011/2016) :\n"))
	age = int(input("\nChoose a starting age (from 0 to 85 five by five) :\n"))
	print("\nIn", year, "there was", statistic.pop_stats(year, age, com_dep[0].upper())[0], "(", statistic.pop_stats(year, age, com_dep[0].upper())[1], "women &", statistic.pop_stats(year, age, com_dep[0].upper())[2], "man ) aged", age, "to", age + 9, "years in", com_dep[0].upper(), "\n")

if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument("--dbreset", help="Reset databases", action="store_true")
	args = parser.parse_args()

	if args.dbreset:
		main(dbreset = True)
	else:
		main()





