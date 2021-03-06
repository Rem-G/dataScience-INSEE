import os
from pathlib import Path
import sqlite3
import pandas as pd
import requests


class Statistic():

	def __init__(self):
		self.code_insee = None
		parent_dir = Path(os.getcwd()).parent
		self.db = str(Path.joinpath(parent_dir, "data", "population_1968-2016.db"))

	def auth_api(self, url):
		token_auth = '0f045f2a33890a5e3b11911fff10efc9918c0785d7665299a8c8fa1d'

		headers = {'Authorization': token_auth}
		response = requests.get(url, headers=headers)
		return response

	def com_info(self, city, dep):
		"""
		This function outputs the general information about one city given its name and its department number
		:param city: name of the city
		:param dep: code of the department
		:return: city name, city's zip code, city's INSEE code, city's area, city's population, city's population's density
		"""
		url = 'https://geo.api.gouv.fr/communes/?nom={}&fields=code,nom,surface,codesPostaux,population,departement&json&format=json'

		if 'arrondissement'.upper() in city.upper():
			city = city.split(' ')[0]

		response = self.auth_api(url.format(city)).json()

		if len(response) >= 1:
			data = {}
			for result in response:
				if result['nom'].upper() == city.upper() and result['departement']['code'] == dep:
					data = result

			insee_code = data['code']
			nom_com = data['nom']
			code_postal = " ".join(data['codesPostaux'])

			superficie = round(data['surface'] / 10**2, 3)
			pop = data['population']
			densite = round(pop / superficie, 3)

			return {'nom': nom_com, 'code_postal': code_postal, 'code_insee': insee_code, 'superficie': superficie, 'pop': pop, 'densite': densite}
		return {'nom': "Commune fusionnée, les données pour l'année courante ne sont pas disponibles", 'code_postal': None, 'code_insee': None, 'superficie': None, 'pop': None, 'densite': None}

	def get_dep_name(self, dep):
		"""
		Outputs the department's name given its number
		:param dep: department's code
		:return: department name
		"""
		parent_dir = Path(os.getcwd()).parent
		db = str(Path.joinpath(parent_dir, "data", "population_social_categories_1968-2016.db"))

		conn = sqlite3.connect(db)
		c = conn.cursor()

		c.execute("""SELECT Libelle_dep FROM Departement WHERE Code_departement == '{}'""".format(dep))
		return c.fetchall()[0][0]

	def get_deps(self):
		"""
		Outputs a list of all of France's department's code
		:return:
		"""
		parent_dir = Path(os.getcwd()).parent
		db = Path.joinpath(parent_dir, "data", "population_1968-2016.db")

		conn = sqlite3.connect(self.db)
		c = conn.cursor()
		c.execute("""SELECT Departement_en_geographie_2018 FROM COM_2016 WHERE Departement_en_geographie_2018 != 'DR18'""")
		deps = c.fetchall()

		return [dep[0] for dep in set(deps)]


	def get_communes(self, dep):
		"""
		Outputs all cities' located in one department
		:param dep: department code
		:return: list of all cities in that department
		"""
		parent_dir = Path(os.getcwd()).parent
		db = Path.joinpath(parent_dir, "data", "population_1968-2016.db")

		conn = sqlite3.connect(self.db)
		c = conn.cursor()
		c.execute("""SELECT Libelle_de_commune FROM COM_2016 WHERE Departement_en_geographie_2018 == '{}'""".format(dep))
		communes = c.fetchall()

		return communes

	def get_pop_all_period(self, commune):
		"""
		Outputs a dictionary that contains the population of all year contained in our data base
		:param commune: name of the commune
		:return:
		"""
		conn = sqlite3.connect(self.db)
		c = conn.cursor()
		c.execute("""SELECT name FROM sqlite_master WHERE type = 'table'""")
		tables = c.fetchall()

		population_all_period = dict()

		for table in tables:
			sql = 'SELECT population, pop_men, pop_women FROM {} WHERE Libelle_de_commune = "{}"'.format(table[0], commune)
			c.execute(sql)
			result = c.fetchall()
			if len(result) and result[0][0] is not None:
				population_all_period[table[0].split("_")[1]] = result[0]

		return population_all_period

	def get_years(self):
		"""
		Outputs a list of all the years at which we possess data
		:return:
		"""
		conn = sqlite3.connect(self.db)
		c = conn.cursor()
		c.execute("""SELECT name FROM sqlite_master WHERE type = 'table'""")
		tables = c.fetchall()

		return [int(table[0].split('_')[1]) for table in tables]

	def get_largest_age_group(self, year, city):
		"""
		Outputs the most represented age-group given a city name and a year
		:param year:
		:param city:
		:return:
		"""

		age_group = [0, 0, 0] # population, age_start, age_end
		age_group_w = [0, 0, 0]
		age_group_m = [0, 0, 0]

		for age in range(0, 91, 5):

			res = self.pop_stats(year, age, city)

			pop = res[0]
			pop_w = res[1]
			pop_m = res[2]

			if pop >= age_group[0]:
				age_group[0] = pop
				age_group[1] = age
				age_group[2] = age + 9

			elif pop_w >= age_group_w[0]:
				age_group_w[0] = pop_w
				age_group_w[1] = age
				age_group_w[2] = age + 9

			elif pop_m >= age_group_m[0]:
				age_group_m[0] = pop_m
				age_group_m[1] = age
				age_group_m[2] = age + 9

		if age_group != [0]*3 or age_group_w != [0]*3 or age_group_m != [0]*3:
			return (age_group, age_group_w, age_group_m)
		return (None, None, None)

	def pop_stats(self, year, age, city):
		"""
		Outputs the population of a given age group given a year, a city name
		:param year:
		:param age:
		:param city:
		:return: population of men, women and both
		"""

		filename = str(Path(os.getcwd()).parent) + "/data/population_1968-2016.db"
		conn = sqlite3.connect(filename)
		cursor = conn.cursor()

		table = "COM_" + str(year)
		sum_women, sum_men = 0, 0

		try:
			if age == 90 : # The name of the column is different once passed 90 years old
				for row in cursor.execute("SELECT De_" + str(age) + "_a_" + str(age + 4) + "_ans_Femmes_RP" + str(year) + ", De_" + str(age) + "_a_" + str(age + 4) + "_ans_Hommes_RP" + str(year) + ", " + table + ".'" + str(age + 5) + "_ans_et_plus_Femmes_RP" + str(year) + "', " + table + ".'" + str(age + 5) + "_ans_et_plus_Hommes_RP" + str(year) + "' FROM " + table + " WHERE " + table + ".Libelle_de_commune LIKE '" + city[0].upper() + city[1::].lower() + "'"):
					if str(row[0]) != 'None' and str(row[1]) != 'None':
						sum_women += float(str(row[0])) + float(str(row[2]))
						sum_men += float(str(row[1])) + float(str(row[3]))

			else:
				for row in cursor.execute("SELECT De_" + str(age) + "_a_" + str(age + 4) + "_ans_Femmes_RP" + str(year) + ", De_" + str(age) + "_a_" + str(age + 4) + "_ans_Hommes_RP" + str(year) + ", De_" + str(age + 5) + "_a_" + str(age + 9) + "_ans_Femmes_RP" + str(year) + ", De_" + str(age + 5) + "_a_" + str(age + 9) + "_ans_Hommes_RP" + str(year) + " FROM " + table + " WHERE " + table + ".Libelle_de_commune LIKE '" + city[0].upper() + city[1::].lower() + "'"):
					if str(row[0]) != 'None' and str(row[1]) != 'None':
						sum_women += float(str(row[0])) + float(str(row[2]))
						sum_men += float(str(row[1])) + float(str(row[3]))

			return(int(sum_women) + int(sum_men), int(sum_women), int(sum_men))

		except:
			return (None, None, None)

	def category_soc_pro(self, year, city):
		"""
		Outputs the number of workers in all socio professional categories given a year adn a city name
		:param year:
		:param city:
		:return:
		"""

		filename = str(Path(os.getcwd()).parent) + "/data/population_social_categories_1968-2016.db"
		conn = sqlite3.connect(filename)
		cursor = conn.cursor()

		table = "COM_" + str(year)
		result = {}
		columns = [row[0] for row in cursor.execute("SELECT name FROM PRAGMA_TABLE_INFO('"+ table + "')")]

		for row in cursor.execute("SELECT * FROM " + table + " WHERE " + table + ".Libelle_de_commune LIKE '" + city[0].upper() + city[1::].lower() + "'"):
			for i in range(len(row)):
				if row[i] != 'None':
					result[columns[i]] = row[i]

		return result

	def get_actif(self, city, year):
		"""
		Outputs the number of active people given a city name and a year
		:param city:
		:param year:
		:return:
		"""

		filename = str(Path(os.getcwd()).parent) + "/data/population_social_categories_1968-2016.db"
		conn = sqlite3.connect(filename)
		cursor = conn.cursor()

		table = "COM_" + str(year)
		nb_travailleur = 0

		try:
			for row in cursor.execute("SELECT * FROM " + table + " WHERE " + table + ".Libelle_de_commune LIKE '" + city[0].upper() + city[1::].lower() + "'"):
				for i in range(2, len(row)):
					if row[i] != 'None':
						nb_travailleur += float(row[i])

			return nb_travailleur
		except:
			return None

	def get_chomeur(self, city, year):
		"""
		Outputs the number of inactive people given a city name and a year
		:param city:
		:param year:
		:return:
		"""

		filename = str(Path(os.getcwd()).parent) + "/data/population_social_categories_1968-2016.db"
		conn = sqlite3.connect(filename)
		cursor = conn.cursor()

		table = "COM_" + str(year)
		nb_chomeur = 0
		city = str(city)

		try:
			for row in cursor.execute("SELECT Agriculteurs_Chomeurs_RP" + str(year) + ", \"Artisans,_commercants,_chefs_d'entreprise_Chomeurs_RP" + str(year) + "\", Cadres_et_professions_intellectuelles_superieures_Chomeurs_RP" + str(year) + ", Professions_intermediaires_Chomeurs_RP" + str(year) + ", Employes_Chomeurs_RP" + str(year) + ", Ouvriers_Chomeurs_RP" + str(year) + " FROM " + table + " WHERE " + table + ".Libelle_de_commune LIKE '" + city[0].upper() + city[1::].lower() + "'"):
				for value in row:
					if value != 'None':
						nb_chomeur += float(value)

			return nb_chomeur
		except:
			return None

	def category_soc_pro_dep(self, year, city):
		"""
		Outputs the number of workers in all socio professional categories in one department (determined by the city given)
		:param year:
		:param city:
		:return:
		"""

		filename = str(Path(os.getcwd()).parent) + "/data/population_social_categories_1968-2016.db"
		conn = sqlite3.connect(filename)
		cursor = conn.cursor()

		table = "COM_" + str(year)
		dep = self.category_soc_pro(year, city)['Departement_en_geographie_2018']
		columns = [row[0] for row in cursor.execute("SELECT name FROM PRAGMA_TABLE_INFO('" + table + "')")]
		result = {}

		for row in cursor.execute("SELECT * FROM " + table + " WHERE " + table + ".Departement_en_geographie_2018 LIKE " + dep):
			for i in range(2, len(row)):
				if row[i] != 'None' or row[i] is not None:
					if columns[i] in result.keys():
						result[columns[i]] += float(str(row[i]).replace('None', '0'))
					else:
						result[columns[i]] = float(str(row[i]).replace('None', '0'))

		max_key = max(result, key = result.get)
		max_value = int(max(result.values()))

		return max_key, max_value

	def category_soc_pro_max_dep(self, year, city):
		"""
		Outputs the most represented socio professional category in one department
		:param year:
		:param city:
		:return:
		"""

		filename = str(Path(os.getcwd()).parent) + "/data/population_social_categories_1968-2016.db"
		conn = sqlite3.connect(filename)
		cursor = conn.cursor()

		table = "COM_" + str(year)
		dep = self.category_soc_pro(year, city)['Departement_en_geographie_2018']
		columns = [row[0] for row in cursor.execute("SELECT name FROM PRAGMA_TABLE_INFO('" + table + "')")]
		result = {}

		for row in cursor.execute("SELECT * FROM " + table + " WHERE " + table + ".Departement_en_geographie_2018 LIKE " + dep):
			for i in range(2, len(row)):
				if row[i] != 'None' or row[i] is not None:
					if columns[i] in result.keys():
						result[columns[i]] += float(str(row[i]).replace('None', '0'))
					else:
						result[columns[i]] = float(str(row[i]).replace('None', '0'))

		max_key = max(result, key = result.get)
		max_value = int(max(result.values()))

		return max_key, max_value

	def categories_soc_pro_commune(self, commune):
		"""
		Outputs the socioprofessional categries and their workers (DashBoard version)
		:param commune:
		:return:
		"""

		filename = str(Path(os.getcwd()).parent) + "/data/population_social_categories_1968-2016.db"
		conn = sqlite3.connect(filename)
		cursor = conn.cursor()

		cursor.execute("""SELECT name FROM sqlite_master WHERE type = 'table'""")
		tables = cursor.fetchall()
		tables.remove(('Departement',))

		result = {}
		unemployment = {}

		for table in tables:
			columns = [row[0] for row in cursor.execute("SELECT name FROM PRAGMA_TABLE_INFO('" + table[0] + "')")]

			for row in cursor.execute("SELECT * FROM " + table[0] + " WHERE " + table[0] + ".Libelle_de_commune LIKE '" + commune + "'"):
				for i in range(2, len(row)):
					if row[i] != 'None' or row[i] is not None:
						if columns[i] in result.keys():
							result[columns[i]] += float(str(row[i]).replace('None', '0'))
						else:
							result[columns[i]] = float(str(row[i]).replace('None', '0'))

		unemployment = {}
		employment = {}

		for key in result.keys():
			if 'chomeurs' in key.lower():
				unemployment[key] = result[key]
			else:
				employment[key] = result[key]

		return {'years': [table[0].split('_')[1] for table in tables], 'employment': employment, 'unemployment': unemployment}


	def pop_stats_all_period(self, year, city):
		"""
		Outputs all the data we gathered given a city and the year
		:param year:
		:param city:
		:return:
		"""
		filename = str(Path(os.getcwd()).parent) + "/data/population_1968-2016.db"
		conn = sqlite3.connect(filename)
		cursor = conn.cursor()

		table = "COM_" + str(year)

		columns = [row[0] for row in cursor.execute("SELECT name FROM PRAGMA_TABLE_INFO('" + table + "')")]
		columns.remove('Departement_en_geographie_2018')
		columns.remove('Libelle_de_commune')
		columns.remove('population')
		columns.remove('pop_men')
		columns.remove('pop_women')

		sql = "SELECT "
		for column in columns:
			sql += table+".'"+column+"', "

		sql = sql[:len(sql)-2]
		sql += " FROM {} WHERE Libelle_de_commune = '{}'".format(table, city)

		cursor.execute(sql)

		result = cursor.fetchall()[0]

		index = 0
		result_dict = dict()
		for r in result:
			result_dict[columns[index]] = int(float(r))
			index += 1

		return result_dict

	def commerces_com(self, commune, dep):
		"""
		Outputs the data of all shops in that city
		:param commune:
		:param dep:
		:return:
		"""
		filename = str(Path(os.getcwd()).parent) + "/data/equip-serv-commerce-com-2018.csv"
		df = pd.read_csv(filename, sep=';', low_memory=False)

		try:
			dep_lines  = df.loc[df['Département'].str.upper() == dep.upper()]
			line = df.loc[df['Libellé commune ou ARM'].str.upper() == commune.upper()]

			nb_commerces_food = 0
			nb_commerces_other = 0

			for label, content in line.items():
				if label not in ['Unnamed: 0', 'CODGEO', 'Libellé commune ou ARM', 'Région', 'Département']:
					if label in ['Hypermarché', 'Supermarché', 'Supérette', 'Epicerie', 'Boulangerie', 'Boucherie charcuterie', 'Produits surgelés', 'Poissonnerie']:
						nb_commerces_food += int(content.values[0])
					else:
						nb_commerces_other += int(content.values[0])

			return {'food': nb_commerces_food, 'other': nb_commerces_other}
		except:
			return {'food': None, 'other': None}

	def set_code_insee(self, code_insee):
		self.code_insee = code_insee

	def auth_api(self, url):
		token_auth = ''

		headers={'Authorization': token_auth}
		response = requests.get(url, headers=headers)
		return requests.get(url)

	def get_dvf(self, type_local, commerce):
		"""
		Gets all the data from the API
		"""
		if commerce:
			url = "http://api.cquest.org/dvf?code_commune={}&code_type_local={}".format(self.code_insee, 4)
		else:
			url = "http://api.cquest.org/dvf?code_commune={}&type_local={}".format(self.code_insee, type_local)
		return self.auth_api(url).json()

	def get_valeur_local(self, type_local, terrain=False, commerce=False):
		response = self.get_dvf(type_local, commerce)
		type_local_response = list()

		for x in response['resultats']:
			if x['surface_relle_bati'] and x['valeur_fonciere']:
				type_local_response.append(x)

		valeur = surface = mutations_nb = 0
		for res in type_local_response:

			if res['surface_terrain'] and terrain:
				valeur += int(res['valeur_fonciere'])
				surface += int(res['surface_relle_bati']) + int(res['surface_terrain'])
				mutations_nb+=1

			elif not terrain and not res['surface_terrain']:
				valeur += int(res['valeur_fonciere'])
				surface += int(res['surface_relle_bati'])
				mutations_nb+=1

		return {'m2': valeur/surface, 'prix_moy' : valeur/mutations_nb, 'surface_moy': surface/mutations_nb}


		



