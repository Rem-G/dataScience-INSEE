import pandas as pd
import os
from pathlib import Path
import sqlite3

class Data():

	def create_db(self, db_type, origine):
		"""
		db_type True : db_population
		db_type False : db_socialcategories
		"""
		path_excel = str(Path(os.getcwd()).parent) + "/data/" + origine
		com_dates = ["COM_1968", "COM_1975", "COM_1982", "COM_1990", "COM_1999", "COM_2006", "COM_2011", "COM_2016"]

		if db_type:
			filename = str(Path(os.getcwd()).parent) + "/data/population_1968-2016.db"
			skiprows = range(12)
			usecols = "E:AT"
		else:
			filename = str(Path(os.getcwd()).parent) + "/data/population_social_categories_1968-2016.db"
			skiprows = range(14)
			usecols = "E:R"

		conn = sqlite3.connect(filename)

		for sheet in com_dates:
			df = pd.read_excel(path_excel, sheet_name = sheet, skiprows = skiprows, usecols = usecols)
			df.columns = df.columns.str.replace(' ', '_')
			df.columns = df.columns.str.replace('\n', '_')

			df.to_sql(sheet, conn, index = False, if_exists = "replace")
			print(sheet, "done")

		conn.commit()
		conn.close()

		print("Done")

	def add_columns(self, db_name):
		conn = sqlite3.connect(db_name)
		c = conn.cursor()

		c.execute("SELECT name FROM sqlite_master WHERE type='table';")
		tables = c.fetchall()

		for table in tables:
			c.execute("ALTER TABLE " + str(table[0]) + " ADD COLUMN pop_men")
			c.execute("ALTER TABLE " + str(table[0]) + " ADD COLUMN pop_women")
			c.execute("ALTER TABLE " + str(table[0]) + " ADD COLUMN population")

		conn.commit()
		conn.close()



	def read_db_population(self, db_name, date, commune, departement):
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

		if len(population):
			for com in population:
				if com[0].upper() == commune.upper():
					return com

		elif not len(population):
			#Communes avec arrondissements : Marseille 1er arrondissement -> Marseille
			c.execute('''SELECT {} FROM COM_{} WHERE replace(replace(replace(replace(replace(replace(upper(Libellé_de_commune), 'É','E'), 'Ê','E'), 'È','E'), 'é','E'), 'ê','E'), 'è', 'E') LIKE upper('%{}%') AND Département_en_géographie_2018 LIKE '{}' '''.format(sql_command, date, commune.split(" ")[0], departement))
			population = c.fetchall()

			try:
				return [int(population[0][1]), "Any data available for {}, data for {}".format(commune, commune.split(" ")[0])]
			except:
				return "Any data available for this date"


