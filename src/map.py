import sqlite3
from pathlib import Path
import os
import requests
import json
import pandas as pd
import math
from bs4 import BeautifulSoup
import numpy as np
import folium
from branca.colormap import *
import re


class MapDVF():
	def OSM_init(self, coordinates):
		self.osm_map = folium.Map(
			location = coordinates,
			zoom_start = 8,
			tiles = 'Stamen Terrain',
			)

	def get_deps(self):
		"""
		return all departements available in the database
		"""
		parent_dir = Path(os.getcwd()).parent
		db = str(Path.joinpath(parent_dir, "data", "population_1968-2016.db"))

		conn = sqlite3.connect(db)
		c = conn.cursor()
		c.execute("""SELECT Departement_en_geographie_2018 FROM COM_2016 WHERE Departement_en_geographie_2018 != 'DR18'""")
		deps = c.fetchall()

		return [dep[0] for dep in set(deps)]#set -> avoid duplicates, [0] -> fetchall returns (dep, None)

	def auth_api(self, url):
		token_auth = ''

		headers={'Authorization': token_auth}
		response = requests.get(url, headers=headers)
		return requests.get(url)


	def get_communes(self, dep):
		"""
		:param dep str: Dep to search
		:return code_dict dict: Return a dict of cities in the format code_insee : features
		"""
		url = "https://geo.api.gouv.fr/departements/{}/communes?fields=nom,code,codesPostaux&format=geojson&geometry=contour".format(dep)
		response = self.auth_api(url).json()

		code_dict = {x['properties']['code']: x for x in response['features']}
		return code_dict


	def get_valeur_local(self, response):
		"""
		:param reponse pendas dataframe:
		:return list:
		Return the m2 price for the most present type of local in the city
		"""
		maison_response = list()
		appartement_response = list()
		type_local = None

		for index, row in response.iterrows():
			if not pd.isnull(response.loc[index, 'surface_reelle_bati']) and not pd.isnull(response.loc[index, 'valeur_fonciere']) and (row['type_local'] == 'Maison'):
				maison_response.append(row)

			if not pd.isnull(response.loc[index, 'surface_reelle_bati']) and not pd.isnull(response.loc[index, 'valeur_fonciere']) and (row['type_local'] == 'Appartement'):
				appartement_response.append(row)

		if len(maison_response) > len(appartement_response):
			type_local_response = maison_response
			type_local = "Maison"
		else:
			type_local_response = appartement_response
			type_local = "Appartement"

		valeur = surface = mutations_nb = 0
		for res in type_local_response:
			valeur += int(res['valeur_fonciere'])
			mutations_nb += 1

			if not math.isnan(res['surface_terrain']):
				surface += int(res['surface_reelle_bati']) + int(res['surface_terrain'])

			else:
				surface += int(res['surface_reelle_bati'])

		if valeur > 0 and surface > 0:
			return {'m2': valeur/surface, 'surface_moy': surface/mutations_nb, 'type_local': type_local}    

	def html_scrapper(self, dep):
		"""
		:param dep str: Dep to get
		:return list: Csv cities available
		Scrap te site cadastre.data.gouv.fr to find the cities where DVF is available
		"""
		page = requests.get('https://cadastre.data.gouv.fr/data/etalab-dvf/latest/csv/2019/communes/{}/'.format(dep))
		soup = BeautifulSoup(page.text, 'html.parser')
		scrap = soup.findAll('a', href = re.compile('\.csv$'))

		return [file.getText().split(".")[0] for file in scrap]

	def get_code_postal_insee(self, df):
		"""
		:param df pandas dataframe:
		:return list: Return all codes_postal and code_insee available in the dataframe of a city
		"""
		try:
			code_postal = df['code_postal'].iloc[0]
			code_insee = df['code_commune'].iloc[0]

			i = j = 0
			if not isinstance(code_postal, str):#When the code_postal is right, we have a str
				while np.isnan(code_postal):
					i += 1
					code_postal = df['code_postal'].iloc[i]
				code_postal = str(int(code_postal))

				if len(code_postal) == 4:#if dep begins with 0 -> 0 has been dropped
					code_postal = '0'+code_postal

			if not isinstance(code_insee, str):
				while np.isnan(code_insee):
					j += 1
					code_insee = df['code_commune'].iloc[j]
				code_insee = str(int(code_insee))

				if len(code_insee) == 4:
					code_insee = '0'+code_insee

			return [code_postal, code_insee]

		except:
			return [None]*2


	def update_dvf_values(self, com, local_dvf_values, dvf_values, communes, cpt_codes, code_postal, code_insee):
		"""
		:param com str: com to update
		:param local_dvf_values dict: dvf values of the city
		:param dvf_values dict: Condensed dvf values of the city
		:param communes dict: Cities of dep
		:param cpt_codes int: Number of dvf entities summed 
		:param code_postal  str:
		:param code_insee str:

		Arrondissements have different code_postal but the same code_insee
		update_dvf_values loops in all the code_postal to sum the arrondissement indicators to only one city
		Example : Paris 1er, Paris 2e, ... -> Paris
		We have to use this solution because we do not always have the arrondissements geometry or data
		"""
		if code_insee not in communes.keys():#Unknown code_insee, we have to find his city
			for commune_code in communes.keys():

				if code_postal in communes[commune_code]['properties']['codesPostaux']:#Look for the city of code_insee
					commune = communes[commune_code]
					com = commune['properties']['code']
					com_values = {'geometry': commune['geometry']}

					if com in dvf_values.keys():#Sum of the current indicators -> we link all code_postal to a code_insee
						dvf_values[com]['valeur_locaux']['m2'] += local_dvf_values['m2']

						dvf_values[com]['commune'] = commune['properties']['nom']
					else:
						com_values = {'geometry': commune['geometry']}

						com_values['valeur_locaux'] = local_dvf_values
						dvf_values[com] = com_values
						dvf_values[com]['commune'] = commune['properties']['nom']

					commune['properties']['codesPostaux'].remove(code_postal)
					cpt_codes += 1

					if not len(commune['properties']['codesPostaux']):
						dvf_values[com]['valeur_locaux']['m2'] = dvf_values[com]['valeur_locaux']['m2']/cpt_codes
						cpt_codes = 0
		
		else:
			#code_insee exists in our communes
			com_values = {'geometry': communes[code_insee]['geometry']}
			com_values['valeur_locaux'] = local_dvf_values
			dvf_values[com] = com_values
			dvf_values[com]['commune'] = communes[code_insee]['properties']['nom']

		return [dvf_values, cpt_codes]

	def get_dvf(self, dep):
		"""
		:param dep string:
		:return dvf_values dict: All dvf values for the dep
		"""
		dvf_values = dict()
		communes = self.get_communes(dep)
		communes_scrap = self.html_scrapper(dep)
		cpt_codes = 0

		for com in communes_scrap:
			print("Dep", dep, "Commune : ", communes_scrap.index(com)+1, "/", len(communes_scrap), end='\r')

			url_csv = 'https://cadastre.data.gouv.fr/data/etalab-dvf/latest/csv/2019/communes/{}/{}.csv'.format(dep, com)
			df = pd.read_csv(url_csv)

			code_postal, code_insee = self.get_code_postal_insee(df)

			if code_postal and code_insee:
				local_dvf_values = self.get_valeur_local(df)
				if local_dvf_values:
					dvf_values, cpt_codes = self.update_dvf_values(com, local_dvf_values, dvf_values, communes, cpt_codes, code_postal, code_insee)

		return dvf_values

	def get_color(self, feature, data):
		"""
		:param feature dict:
		:param data pandas dataframe:
		Return a variation of color depending on the color scale of the dep data
		"""
		map_dict = data.set_index('code_com')['m2'].to_dict()
		val_max = max(map_dict.values())
		val_min = min(map_dict.values())

		color_scale = LinearColormap(['white','red'], index=[val_min, 100*np.log(val_max)], vmin = val_min, vmax = 100*np.log(val_max))

		value = map_dict.get(feature['code_com'])
		if value is None:
			return '#8c8c8c' # MISSING -> gray
		else:
			return color_scale(value)

	def add_layers(self, geojson_data, data):
		"""
		Add layers on the folium map
		:param geojson_data dict: polygon to add on the map
		:param data pandas dataframe: data to display on the map
		"""
		map_dict = data.set_index('code_com')['m2'].to_dict()
		val_max = max(map_dict.values())
		val_min = min(map_dict.values())

		for temp_feature in geojson_data["features"]:
			temp_geojson = {"features":[temp_feature],"type":"FeatureCollection"}

			temp_layer = folium.GeoJson(
			data = temp_geojson,
			style_function = lambda feature: {
				'fillColor': self.get_color(feature, data),
				'fillOpacity': 0.7,
				'color' : 'black',
				'weight' : 1,
				},
			)

			html="""
			    	<h4 style="font-family: Avenir, sans-serif;">Commune : </h4>
			    	<span style="font-family: Avenir, sans-serif;">{}</span>
			    	<h4 style="font-family: Avenir, sans-serif;">Type logement : </h4>
			    	<span style="font-family: Avenir, sans-serif;">{}</span>
			    	<h4 style="font-family: Avenir, sans-serif;">Prix moyen m2 : </h4>
			    	<span style="font-family: Avenir, sans-serif;">{}€</span>
			    """.format(str(temp_feature['commune']), temp_feature['properties']['type_local'], str(int(map_dict[temp_feature['code_com']])))

			iframe = folium.IFrame(html=html, width=150, height=250)
			folium.Popup(iframe, min_width=200).add_to(temp_layer)
			temp_layer.add_to(self.osm_map)

		LinearColormap(['white','red'], index=[val_min, 100*np.log(val_max)], vmin = val_min, vmax = 100*np.log(val_max)).add_to(self.osm_map)#LEGEND

	def create_map_dep(self, dep):
		"""
		:param dep str:
		Create the map with DVF data for dep
		"""
		dvf_dep = self.get_dvf(dep)

		first_com = list(dvf_dep.keys())[0]
		url_dep_center = 'https://geo.api.gouv.fr/communes/{}?format=geojson&geometry=center'.format(first_com)
		response = self.auth_api(url_dep_center).json()
		center_coordinates = response['geometry']['coordinates']

		self.OSM_init(center_coordinates[::-1])

		geojson_collection = {'type':'FeatureCollection', 'features':[]}
		data = dict()
		data['code_com'] = list()
		data['m2'] = list()

		for com in dvf_dep.keys():

			feature = {'type' : 'Feature', 'commune': dvf_dep[com]['commune'], 'code_com': com, 'properties': {'name': com, 'type_local': dvf_dep[com]['valeur_locaux']['type_local']}}
			feature['geometry'] = dvf_dep[com]['geometry']
			geojson_collection['features'].append(feature)

			data['code_com'].append(com)
			data['m2'].append(dvf_dep[com]['valeur_locaux']['m2'])

		df = pd.DataFrame (data, columns = ['code_com', 'm2'])
		self.add_layers(geojson_collection, df)

		parent_dir = Path(os.getcwd()).parent
		file = Path.joinpath(parent_dir, "static", "maps", "{}.html".format(dep))
		self.osm_map.save(str(file))

	def map_main(self, maps_reset = False):
		deps = self.get_deps()
		deps.remove("57")
		deps.remove("67")
		deps.remove("68")
		#/!\ NO DVF DATA FOR DEPS 57, 67, 68 /!\
		for dep in deps:
			if maps_reset or not Path.joinpath(Path(os.getcwd()).parent, "static", "maps", "{}.html".format(dep)).is_file():
				print("\n", "Département : ", dep, (deps.index(dep)/len(deps))*100, ' %')
				self.create_map_dep(dep)

#m.create_map_dep("57")



