import os
from pathlib import Path
import sqlite3

class Statistic():

	def get_je_sais_pas_quoi(self, year):

		filename = str(Path(os.getcwd()).parent) + "/data/population_1968-2016.db"
		conn = sqlite3.connect(filename)
		cursor = conn.cursor()

		table = "COM_" + str(year)
		pass



	def pop_stats(self, year, age, city):

		filename = str(Path(os.getcwd()).parent) + "/data/population_1968-2016.db"
		conn = sqlite3.connect(filename)
		cursor = conn.cursor()

		table = "COM_" + str(year)
		sum_women, sum_men = 0, 0

		for row in cursor.execute("SELECT De_" + str(age) + "_a_" + str(age + 4) + "_ans_Femmes_RP" + str(year) + ", De_" + str(age) + "_a_" + str(age + 4) + "_ans_Hommes_RP" + str(year) + ", De_" + str(age + 5) + "_a_" + str(age + 9) + "_ans_Femmes_RP" + str(year) + ", De_" + str(age + 5) + "_a_" + str(age + 9) + "_ans_Hommes_RP" + str(year) + " FROM " + table + " WHERE " + table + ".Libelle_de_commune LIKE '" + city[0].upper() + city[1::].lower() + "'"):
			if str(row[0]) != 'None' and str(row[1]) != 'None':
				sum_women += float(str(row[0])) + float(str(row[2]))
				sum_men += float(str(row[1])) + float(str(row[3]))

		return(int(sum_women) + int(sum_men), int(sum_women), int(sum_men))