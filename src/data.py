import pandas as pd
import pandas as pd
import os
from pathlib import Path
import sqlite3
from unidecode import unidecode
import time
import datetime

class Data():

	def create_db(self, db_type, origine):
		"""
		db_type True : db_population
		db_type False : db_socialcategories
		"""
		parent_dir = Path(os.getcwd()).parent
		path_excel = Path.joinpath(parent_dir, "data", origine)
		com_dates = ["COM_1968", "COM_1975", "COM_1982", "COM_1990", "COM_1999", "COM_2006", "COM_2011", "COM_2016"]

		if db_type:
			filename = Path.joinpath(parent_dir, "data", "population_1968-2016.db")
			#filename = str(Path(parent_dir + "/data/population_1968-2016.db"))
			try:
				os.remove(filename)
			except:
				pass

			skiprows = range(12)
			usecols = "E:AT"
		else:
			filename = Path.joinpath(parent_dir, "data", "population_social_categories_1968-2016.db")

			#filename = str(Path(parent_dir + "/data/population_social_categories_1968-2016.db"))
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

				if index > 0:
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

	def read_db_population(self, db_name, date, commune, departement):
		#ages_pop = ["De 0 à 4 ans", "De 5 à 9 ans", "De 10 à 14 ans", "De 15 à 19 ans", "De 20 à 24 ans", "De 25 à 29 ans", "De 30 à 34 ans", "De 35 à 39 ans", "De 40 à 44 ans", "De 45 à 49 ans", "De 50 à 54 ans", "De 55 à 59 ans", "De 60 à 64 ans", "De 55 à 59 ans", "De 70 à 74 ans", "De 75 à 79 ans", "De 80 à 84 ans", "De 85 à 89 ans", "De 90 à 94 ans", "95 ans et plus"]

		conn = sqlite3.connect(db_name)
		c = conn.cursor()

		c.execute('''SELECT Libelle_de_commune, population FROM COM_{} WHERE upper(replace(replace(replace(replace(replace(replace(Libelle_de_commune, 'É','E'), 'Ê','E'), 'È','E'), 'é','e'), 'ê','e'), 'è', 'e')) LIKE upper('%{}%') AND Departement_en_geographie_2018 LIKE '{}' '''.format(date, commune, departement))

		population = c.fetchall()

		print(population)

		if len(population):
			for com in population:
				if unidecode(com[0]).upper() == commune.upper():
					return com

		elif not len(population):
			#Communes avec arrondissements : Marseille 1er arrondissement -> Marseille
			c.execute('''SELECT Libelle_de_commune, population FROM COM_{} WHERE upper(replace(replace(replace(replace(replace(replace(Libelle_de_commune, 'É','E'), 'Ê','E'), 'È','E'), 'é','e'), 'ê','e'), 'è', 'e')) LIKE upper('%{}%') AND Departement_en_geographie_2018 LIKE '{}' '''.format(date, commune.split(" ")[0], departement))
			population = c.fetchall()

			try:
				return [int(population[0][1]), "No data available for {}, data for {}".format(commune, commune.split(" ")[0])]
			except:
				return None # No data available for this date


