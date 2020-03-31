import os
from pathlib import Path
import sqlite3

class Statistic():
	def pop_stats(self, year):

		filename = str(Path(os.getcwd()).parent) + "/data/population_1968-2016.db"
		conn = sqlite3.connect(filename)
		cursor = conn.cursor()

		table = "COM_" + str(year)
		sum_women, sum_men = 0, 0
		# J'aimerais afficher toute les tranche d'âge ou permettre de choisir lesquelles afficher
		for row in cursor.execute("SELECT De_20_a_24_ans_Femmes_RP" + str(year) + ", De_20_a_24_ans_Hommes_RP" + str(year) + " FROM " + table + " EXCEPT SELECT De_20_a_24_ans_Femmes_RP" + str(year) + ", De_20_a_24_ans_Hommes_RP" + str(year) + " FROM " + table + " WHERE ROWID = 1"):
			if str(row[0]) != 'None' and str(row[1]) != 'None':
				sum_women += float(str(row[0]))
				sum_men += float(str(row[1]))

		return(int(sum_women), int(sum_men))