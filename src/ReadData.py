import pandas as pd
import os
from pathlib import Path
import json
import requests
import sqlite3


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

def create_db_population():
	path_excel = str(Path(os.getcwd()).parent) + "/data/pop-sexe-age-quinquennal6816.xls"
	com_dates = ["COM_1968", "COM_1975", "COM_1982", "COM_1990", "COM_1999", "COM_2006", "COM_2011", "COM_2016"]

	filename = str(Path(os.getcwd()).parent) + "/data/population_1968-2016.db"

	conn = sqlite3.connect(filename)

	for sheet in com_dates:
		df = pd.read_excel(path_excel, sheet_name = sheet, skiprows = range(12), usecols = "E:AT")
		df.columns = df.columns.str.replace(' ', '_')
		df.columns = df.columns.str.replace('\n', '_')

		df.to_sql(sheet, conn, index = False, if_exists = "replace")
		print(sheet)

	conn.commit()
	conn.close()

	print("Done")

def read_db_population(db_name, date, commune, departement):
	ages_pop = ["De 0 à 4 ans", "De 5 à 9 ans", "De 10 à 14 ans", "De 15 à 19 ans", "De 20 à 24 ans", "De 25 à 29 ans", "De 30 à 34 ans", "De 35 à 39 ans", "De 40 à 44 ans", "De 45 à 49 ans", "De 50 à 54 ans", "De 55 à 59 ans", "De 60 à 64 ans", "De 55 à 59 ans", "De 70 à 74 ans", "De 75 à 79 ans", "De 80 à 84 ans", "De 85 à 89 ans", "De 90 à 94 ans", "95 ans et plus"]
	genders_pop = ["Hommes", "Femmes"]

	list_columns = list()

	for age in ages_pop:
		for gender in genders_pop:
			list_columns.append('"' + age.replace(" ", "_") + "_" + gender + "_" + "RP" + date + '"')

	sql_command = "Libellé_de_commune, "

	for column in list_columns:
		sql_command += "CAST(" + column + " AS FLOAT) + "

	sql_command = sql_command[:len(sql_command)-3]

	conn = sqlite3.connect(db_name)
	c = conn.cursor()

	c.execute('''SELECT {} FROM COM_{} WHERE replace(replace(replace(replace(replace(replace(upper(Libellé_de_commune), 'É','E'), 'Ê','E'), 'È','E'), 'é','E'), 'ê','E'), 'è', 'E') LIKE upper('%{}%') AND Département_en_géographie_2018 LIKE '{}' '''.format(sql_command, date, commune, departement))

	population = c.fetchall()

	print(population)

	if len(population):
		for com in population:
			if com[0].upper() == commune.upper():
				return com

	elif not len(population):
		c.execute('''SELECT {} FROM COM_{} WHERE replace(replace(replace(replace(replace(replace(upper(Libellé_de_commune), 'É','E'), 'Ê','E'), 'È','E'), 'é','E'), 'ê','E'), 'è', 'E') LIKE upper('%{}%') AND Département_en_géographie_2018 LIKE '{}' '''.format(sql_command, date, commune.split(" ")[0], departement))
		population = c.fetchall()

		try:
			return [int(population[0][1]), "Any data available for {}, data for {}".format(commune, commune.split(" ")[0])]
		except:
			return "Any data available for this date"


#create_db_population()
com_dep = user_request()
population = read_db_population(str(Path(os.getcwd()).parent) + "/data/population_1968-2016.db", "2011", com_dep[0], com_dep[1])

print(population, "POPULATION")

