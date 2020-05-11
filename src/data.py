import requests
import json
import pandas as pd
import os
from pathlib import Path
import sqlite3
from unidecode import unidecode
import time
import datetime

class Data():

	def create_db(self, origine):
		"""
		db_type True : db_population
		db_type False : db_socialcategories
		:param origine str: filename to create db
		"""
		parent_dir = Path(os.getcwd()).parent
		path_excel = Path.joinpath(parent_dir, "data", origine)
		com_dates = ["COM_1968", "COM_1975", "COM_1982", "COM_1990", "COM_1999", "COM_2006", "COM_2011", "COM_2016"]

		if 'pop-sexe-age-quinquennal6816.xls' in origine:
			filename = Path.joinpath(parent_dir, "data", "population_1968-2016.db")
			try:
				os.remove(filename)
			except:
				pass

			skiprows = range(12)
			usecols = "E:AT"
		elif 'pop-socialcategories.xls' in origine:
			filename = Path.joinpath(parent_dir, "data", "population_social_categories_1968-2016.db")
			try:
				os.remove(filename)
			except:
				pass

			skiprows = range(14)
			usecols = "E:R"

		conn = sqlite3.connect(filename)

		for sheet in com_dates:
			df = pd.read_excel(path_excel, sheet_name = sheet, skiprows = skiprows, usecols = usecols)
			df.columns = df.columns.str.normalize('NFKD').str.encode('ascii', errors='ignore').str.decode('utf-8')
			df.columns = df.columns.str.replace(' ', '_')
			df.columns = df.columns.str.replace('\n', '_')

			cpt = 0

			row_pop = float(0)
			row_pop_women = float(0)
			row_pop_men = float(0)

			date = "RP"+sheet.split("_")[1]
			rows = df.iterrows()
			columns = df.columns[2:]

			for index, row in rows:
				print(str(filename).split("/")[::-1][0], 'Table', sheet, 'Done', round((cpt/len(df.index))*100, 2), '%', 'Total done', round( ( (cpt + len(df.index)*com_dates.index(sheet))/ (len(df.index)*len(com_dates)) )*100, 2), '%', end='\r')
				cpt += 1

				if index > 0 and 'pop-sexe-age-quinquennal6816.xls' in origine:#drop first row
					for column in columns:
						if "Femmes" in column:
							row_pop_women += float(row[column])
						elif "Hommes" in column:
							row_pop_men += float(row[column])

					row_pop = row_pop_men + row_pop_women
					df.loc[index, 'pop_men'] = row_pop_men
					df.loc[index, 'pop_women'] = row_pop_women
					df.loc[index, 'population'] = row_pop

					row_pop = row_pop_women = row_pop_men = float(0)

			df.to_sql(sheet, conn, index = False, if_exists = "replace")

		conn.commit()
		conn.close()

	def add_departement(self):
		db_name = str(Path(os.getcwd()).parent) + "/data/population_social_categories_1968-2016.db"

		conn = sqlite3.connect(db_name)
		c = conn.cursor()
		c.execute("SELECT name FROM sqlite_master WHERE type='table';")
		tables = c.fetchall()

		c.execute("SELECT DISTINCT Departement_en_geographie_2018 FROM {}".format('COM_2016'))
		dep_number = c.fetchall()
		dep_number = dep_number[1:]

		data = {'Code_departement' : [], 'Libelle_dep' : []}
		for dep in dep_number:
			url = "https://geo.api.gouv.fr/departements/{}".format(dep[0])
			result = requests.get(url).json()
			data['Code_departement'].append(result['code'])
			data['Libelle_dep'].append(result['nom'])

		df = pd.DataFrame(data)
		df.to_sql("Departement", conn, index=False, if_exists="replace")

		conn.commit()
		conn.close()