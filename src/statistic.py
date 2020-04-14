import os
from pathlib import Path
import sqlite3

class Statistic():

	def get_largest_age_group(self, year, city):

		age_group = [0, 0, 0] # population, age_start, age_end
		age_group_w = [0, 0, 0]
		age_group_m = [0, 0, 0]

		for age in range(0, 91, 5):

			pop = self.pop_stats(year, age, city)[0]
			pop_w = self.pop_stats(year, age, city)[1]
			pop_m = self.pop_stats(year, age, city)[2]

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

		return (age_group, age_group_w, age_group_m)

	def pop_stats(self, year, age, city):

		filename = str(Path(os.getcwd()).parent) + "/data/population_1968-2016.db"
		conn = sqlite3.connect(filename)
		cursor = conn.cursor()

		table = "COM_" + str(year)
		sum_women, sum_men = 0, 0

		if age == 90 :
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