import pandas as pd
import os
from pathlib import Path
import sqlite3
from unidecode import unidecode

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
			try:
				os.remove(filename)
			except:
				pass

			skiprows = range(12)
			usecols = "E:AT"
		else:
			filename = str(Path(os.getcwd()).parent) + "/data/population_social_categories_1968-2016.db"
			try:
				os.remove(filename)
			except:
				pass

			skiprows = range(14)
			usecols = "E:R"

		conn = sqlite3.connect(filename)

		for sheet in com_dates:
			df = pd.read_excel(path_excel, sheet_name = sheet, skiprows = skiprows, usecols = usecols)
			#Or NKFD ?
			df.columns = df.columns.str.normalize('NFKC').str.encode('ascii', errors='ignore').str.decode('utf-8')
			df.columns = df.columns.str.replace(' ', '_')
			df.columns = df.columns.str.replace('\n', '_')
			print(df.columns)

			df.to_sql(sheet, conn, index = False, if_exists = "replace")
			print(sheet, "done")

		conn.commit()
		conn.close()

		print("Done")

	def add_columns(self, db_name):
			# ages_pop = ["De 0 à 4 ans", "De 5 à 9 ans", "De 10 à 14 ans", "De 15 à 19 ans", "De 20 à 24 ans", "De 25 à 29 ans", "De 30 à 34 ans", "De 35 à 39 ans", "De 40 à 44 ans", "De 45 à 49 ans", "De 50 à 54 ans", "De 55 à 59 ans", "De 60 à 64 ans", "De 55 à 59 ans", "De 70 à 74 ans", "De 75 à 79 ans", "De 80 à 84 ans", "De 85 à 89 ans", "De 90 à 94 ans", "95 ans et plus"]
			# genders_pop = ["Hommes", "Femmes"]
			# dates = ["1968", "1975", "1982", "1990", "1999", "2006", "2011", "2016"]
			list_columns = list()

			conn = sqlite3.connect(db_name)
			c = conn.cursor()

			c.execute("SELECT name FROM sqlite_master WHERE type='table';")
			tables = c.fetchall()

			for table in tables:
				sql_command_f = """Libelle_de_commune, """
				sql_command_m = sql_command_f

				columns_cursor = c.execute('select * from {}'.format(table[0]))
				list_columns = [description[0] for description in columns_cursor.description]

				for column in list_columns:
					if "Femmes" in column:
						sql_command_f += """CAST("{}" AS FLOAT) + """.format(column)

					if "Hommes" in column:
						sql_command_m += """CAST("{}" AS FLOAT) + """.format(column)

				sql_command_f = sql_command_f[:len(sql_command_f) - 3] # Gets rid of the last 3 characters ([space] + [space])
				sql_command_m = sql_command_m[:len(sql_command_m) - 3]

				print(sql_command_f)
				print(sql_command_m)

				values_pop_f = c.execute("SELECT {} FROM {}".format(sql_command_f, str(table[0])))
				values_pop_f = c.fetchall()

				values_pop_m = c.execute("SELECT {} FROM {}".format(sql_command_m, str(table[0])))
				values_pop_m = c.fetchall()

				try:
					c.execute("ALTER TABLE " + str(table[0]) + " ADD COLUMN pop_men")
					c.execute("ALTER TABLE " + str(table[0]) + " ADD COLUMN pop_women")
					c.execute("ALTER TABLE " + str(table[0]) + " ADD COLUMN population")
				except:
					pass

				for value in values_pop_f[1:]:  # Drop row LIBELLE:
					if None in value:
						value = (None, "NULL")

					sql = """UPDATE {} SET {} = {} WHERE Libelle_de_commune = "{}" """.format(str(table[0]), "pop_women", str(value[1]), str(value[0]))

					print(sql)
					c.execute(sql)

				for value in values_pop_m[1:]:  # Drop row LIBELLE:
					if None in value:
						value = (None, "NULL")

					sql = """UPDATE {} SET {} = {} WHERE Libelle_de_commune = "{}" """.format(str(table[0]), "pop_men", str(value[1]), str(value[0]))

					print(sql)
					c.execute(sql)

					command_sum = '(SELECT CAST(pop_women AS FLOAT) + CAST(pop_men AS FLOAT) FROM {} WHERE Libelle_de_commune = "{}"'.format(str(table[0]), str(value[0]))
					sql_pop = """UPDATE {} SET {} = {} WHERE Libelle_de_commune = "{}" """.format(str(table[0]), "pop", command_sum, str(value[0]))

			conn.commit()
			conn.close()
		

	def read_db_population(self, db_name, date, commune, departement):
		ages_pop = ["De 0 à 4 ans", "De 5 à 9 ans", "De 10 à 14 ans", "De 15 à 19 ans", "De 20 à 24 ans", "De 25 à 29 ans", "De 30 à 34 ans", "De 35 à 39 ans", "De 40 à 44 ans", "De 45 à 49 ans", "De 50 à 54 ans", "De 55 à 59 ans", "De 60 à 64 ans", "De 55 à 59 ans", "De 70 à 74 ans", "De 75 à 79 ans", "De 80 à 84 ans", "De 85 à 89 ans", "De 90 à 94 ans", "95 ans et plus"]

		conn = sqlite3.connect(db_name)
		c = conn.cursor()

		#print('''SELECT Libelle_de_commune, population FROM COM_{} WHERE upper(replace(replace(replace(replace(replace(replace(Libelle_de_commune, 'É','E'), 'Ê','E'), 'È','E'), 'é','e'), 'ê','e'), 'è', 'e')) LIKE upper('%{}%') AND Departement_en_geographie_2018 LIKE '{}' '''.format(date, commune, departement))

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


