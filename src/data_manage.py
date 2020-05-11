import pandas as pd
import os
from pathlib import Path
import zipfile
import glob

from data import *
from map import *

class DataManage():
	def create_csv_commerces(self):
		"""
		Create csv for shops from the excel file
		"""
		filename = str(Path(os.getcwd()).parent) + "/data/equip-serv-commerce-com-2018"
		df_com = pd.read_excel(filename+'.xls', sheet_name = 'COM', skiprows = range(4), usecols = 'B:AB')

		rows = list(range(50))
		except_rows = list(range(30, 51))
		df_arm = pd.read_excel(filename+'.xls', sheet_name = 'ARM', skiprows = list(set(rows) - set(except_rows)), usecols = 'B:AB')

		df = pd.concat([df_com, pd.DataFrame(df_arm.values.tolist(), columns = df_com.columns.values.tolist())], ignore_index = True)

		df.to_csv(filename+'.csv', header=True, sep=';')

	def manage(self, dbreset, mapsreset):
		"""
		:param dbreset, mapsreset boolean: Elements to force reset
		Check if databases and all the maps are present
		The user may force reset with terminal args --dbreset and --mapsreset
		"""
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

			data.create_db("pop-sexe-age-quinquennal6816.xls")

		if dbreset or not Path.joinpath(parent_dir, "data", "population_social_categories_1968-2016.db").is_file():
			if not Path.joinpath(parent_dir, "data", "pop-socialcategories.xls").is_file():
				with zipfile.ZipFile(Path.joinpath(parent_dir, "data", "pop-socialcategories.xls.zip"), 'r') as zip_ref:
					zip_ref.extractall(Path.joinpath(parent_dir, "data"))

			data.create_db("pop-socialcategories.xls")
			data.add_departement()

		if dbreset or not Path.joinpath(parent_dir, "data", "equip-serv-commerce-com-2018.csv").is_file():
			self.create_csv_commerces()
			print("Shops csv created")

		if mapsreset:
			files = glob.glob(str(Path.joinpath(parent_dir, "static", "maps", "*")))
			for f in files:
			    os.remove(f)

		m = MapDVF().map_main(mapsreset) #If maps are missing, it recreates them