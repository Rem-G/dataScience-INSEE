import pandas as pd
import os
from pathlib import Path
import requests
import json
import zipfile
import argparse
from data import *
from statistic import *
from map import *
from data_manage import *


def auth_api(url):
	token_auth = '0f045f2a33890a5e3b11911fff10efc9918c0785d7665299a8c8fa1d'

	headers={'Authorization': token_auth}
	response = requests.get(url, headers=headers)
	return response

def user_request():
	"""
	Will find the city the user typed in and output its general information
	:return:
	"""
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
			print("No city named", request, " has been found")

		if user_validation.lower() == 'y':
			validation = True
			ligne_5 = None
			global insee_code
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
	print("Name :\n", nom_com, "\n")

	return [nom_com, dep_com]

def version_console():
	"""
	Outputs a selecion of indicators. To find more head towards the Dashboard version
	:return:
	"""
	statistic = Statistic()
	statistic.set_code_insee('74010') # Sets Annecy by default
	data = Data()
	com_dep = user_request()
	parent_dir = str(Path(os.getcwd()).parent)

	year = int(input("\nChoose a year (1968/1975/1982/1990/1999/2006/2011/2016) :\n"))
	age = int(input("\nChoose a starting age (from 0 to 90 five by five) :\n"))
	if age == 90:
		print("\nIn", year, "there was", statistic.pop_stats(year, age, com_dep[0].upper())[0], "(", statistic.pop_stats(year, age, com_dep[0].upper())[1], "women &", statistic.pop_stats(year, age, com_dep[0].upper())[2], "men ) aged", age, "or more in", com_dep[0].upper(), "\n")

	else :
		print("\nIn", year, "there was", statistic.pop_stats(year, age, com_dep[0].upper())[0], "(", statistic.pop_stats(year, age, com_dep[0].upper())[1], "women &", statistic.pop_stats(year, age, com_dep[0].upper())[2], "men ) aged", age, "to", age + 9, "years in", com_dep[0].upper(), "\n")

	age_group = statistic.get_largest_age_group(year, com_dep[0].upper())
	print("The", age_group[0][1], "to", age_group[0][2], "age group is the most represented in", year, "in", com_dep[0].upper(), "with", age_group[0][0], "people.")
	print("For the women, it's the", age_group[1][1], "to", age_group[1][2], "age group that is the most represented that year in", com_dep[0].upper(), "with", age_group[1][0], "women.")
	print("As for the men, the", age_group[2][1], "to", age_group[2][2], "age group is the most represented with", age_group[2][0], "men.\n")

	print("Socio-professional categories and their number of people in", com_dep[0].upper(), ":\n")
	result_soc_pro = statistic.category_soc_pro(year, com_dep[0].upper())
	columns = [key for key in statistic.category_soc_pro(year, com_dep[0].upper()).keys()]
	for key_index in range(2, len(columns)):
		print(str(columns[key_index])[:-7], ":", result_soc_pro[columns[key_index]])

	dep = result_soc_pro['Departement_en_geographie_2018']
	if int(dep[-1]) == 1:
		end = 'st'
	elif int(dep[-1]) == 2:
		end = 'nd'
	elif int(dep[-1]) == 3:
		end = 'rd'
	else:
		end = 'th'
	result_soc_pro_dep = statistic.category_soc_pro_dep(year, com_dep[0].upper())
	print("\nIn the", dep + end, "department, the most represented socio-professional category is : '" + str(result_soc_pro_dep[0])[:-7] + "' with", result_soc_pro_dep[1], "people.")

	statistic.set_code_insee(insee_code)
	print("\n###################\n### DONNEES DVF ###\n###################\n")
	print('m² maison terrain + bati')
	data = statistic.get_valeur_local('Maison', terrain=True)
	print("- m² : ", data['m2'])
	print("- prix moyen : ", data['prix_moy'])
	print("- surface moyenne : ", data['surface_moy'], "\n")

	print('m² maison bati')
	data = statistic.get_valeur_local('Maison')
	print("- m² : ", data['m2'])
	print("- prix moyen : ", data['prix_moy'])
	print("- surface moyenne : ", data['surface_moy'], "\n")

	print('m² appartement terrain + bati')
	data = statistic.get_valeur_local('Appartement', terrain=True)
	print("- m² : ", data['m2'])
	print("- prix moyen : ", data['prix_moy'])
	print("- surface moyenne : ", data['surface_moy'], "\n")

	print('m² appartement bati')
	data = statistic.get_valeur_local('Appartement')
	print("- m² : ", data['m2'])
	print("- prix moyen : ", data['prix_moy'])
	print("- surface moyenne : ", data['surface_moy'], "\n")

	print('m² commerce terrain + bati')
	data = statistic.get_valeur_local('Commerce', terrain=True, commerce=True)
	print("- m² : ", data['m2'])
	print("- prix moyen : ", data['prix_moy'])
	print("- surface moyenne : ", data['surface_moy'], "\n")

	print('m² commerce bati')
	data = statistic.get_valeur_local('Commerce', commerce=True)
	print("- m² : ", data['m2'])
	print("- prix moyen : ", data['prix_moy'])
	print("- surface moyenne : ", data['surface_moy'], "\n")

if __name__ == '__main__':
	params = {'dbreset': False, 'mapsreset': False}

	parser = argparse.ArgumentParser()
	parser.add_argument("--dbreset", help="Reset databases", action="store_true")
	parser.add_argument("--mapsreset", help="Reset stored maps", action="store_true")
	args = parser.parse_args()

	if args.dbreset:
		params['dbreset'] = True

	if args.mapsreset:
		params['mapsreset'] = True

	DataManage().manage(dbreset = params['dbreset'], mapsreset = params['mapsreset'])
	version_console()

