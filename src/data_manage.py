import pandas as pd
import os
from pathlib import Path
import zipfile

from data import *
from map import *

class DataManage():
	def create_csv_commerces(self,):
		filename = str(Path(os.getcwd()).parent) + "/data/equip-serv-commerce-com-2018"
		df_com = pd.read_excel(filename+'.xls', sheet_name = 'COM', skiprows = range(4), usecols = 'B:AB')

		rows = list(range(50))
		except_rows = list(range(30, 51))
		df_arm = pd.read_excel(filename+'.xls', sheet_name = 'ARM', skiprows = list(set(rows) - set(except_rows)), usecols = 'B:AB')

		df = pd.concat([df_com, pd.DataFrame(df_arm.values.tolist(), columns = df_com.columns.values.tolist())], ignore_index = True)

		df.to_csv(filename+'.csv', header=True, sep=';')

	def manage(self, dbreset, mapsreset):
		data = Data()
		parent_dir = Path(os.getcwd()).parent

		if dbreset:
			print("############### \nReset databases \n###############")

			print("This operation may take a while\n")
			if input("Reset databases ? y/n : ").lower() == "n":
				dbreset = False

		if dbreset or not Path.joinpath(parent_dir, "data", "population_1968-2016.db").is_file():
			if not Path.joinpath(parent_dir, "data", "pop-sexe-age-quinquennal6816.xls").is_file():
				with zipfile.ZipFile(Path.joinpath(parent_dir, "data", "pop-sexe-age-quinquennal6816.xls.zip"), 'r') as zip_ref:
					zip_ref.extractall(Path.joinpath(parent_dir, "data"))

			data.create_db(True, "pop-sexe-age-quinquennal6816.xls")

		if dbreset or not Path.joinpath(parent_dir, "data", "population_social_categories_1968-2016.db").is_file():
			if not Path.joinpath(parent_dir, "data", "pop-socialcategories.xls").is_file():
				with zipfile.ZipFile(Path.joinpath(parent_dir, "data", "pop-socialcategories.xls.zip"), 'r') as zip_ref:
					zip_ref.extractall(Path.joinpath(parent_dir, "data"))

			data.create_db(False, "pop-socialcategories.xls")
			data.add_departement()
			self.create_csv_commerces()

		if mapsreset or not Path.joinpath(parent_dir, "static", "maps").is_dir():
			with zipfile.ZipFile(Path.joinpath(parent_dir, "static", "maps.zip"), 'r') as zip_ref:
				zip_ref.extractall(Path.joinpath(parent_dir, "static"))

		m = MapDVF().map_main(mapsreset)