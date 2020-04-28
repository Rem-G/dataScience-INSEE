import pandas as pd
import os
from pathlib import Path
import zipfile

from data import *
from map import *

class DataManage():
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

		if mapsreset or not Path.joinpath(parent_dir, "static", "maps").is_dir():
			with zipfile.ZipFile(Path.joinpath(parent_dir, "static", "maps.zip"), 'r') as zip_ref:
				zip_ref.extractall(Path.joinpath(parent_dir, "static"))

		m = MapDVF().map_main(mapsreset)