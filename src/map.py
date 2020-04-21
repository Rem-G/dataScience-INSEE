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


class map():
	def OSM_init(self, coordinates):
		self.osm_map = folium.Map(
			location = coordinates,
			zoom_start = 10,
			tiles = 'Stamen Terrain',
			)

	def get_dep(self):
		"""
		"""
		parent_dir = Path(os.getcwd()).parent
		db = Path.joinpath(parent_dir, "data", "population_1968-2016.db")

		conn = sqlite3.connect(db)
		c = conn.cursor()
		c.execute("""SELECT Departement_en_geographie_2018 FROM COM_2016""")
		deps = c.fetchall()

		deps_list = list()

		for dep in set(deps):
			deps_list.append(dep[0])

		return deps_list

	def auth_api(self, url):
		token_auth = ''

		headers={'Authorization': token_auth}
		response = requests.get(url, headers=headers)
		return requests.get(url)


	def get_communes(self, dep):
		"""
		"""
		url = "https://geo.api.gouv.fr/departements/{}/communes?fields=nom,code,codesPostaux&format=geojson&geometry=contour".format(dep)
		response = self.auth_api(url).json()

		code_dict = {x['properties']['code']: x for x in response['features']}
		return code_dict


	def get_valeur_local(self, response):
		"""
		"""
		maison_response = list()
		appartement_response = list()


		for index, row in response.iterrows():
			if not pd.isnull(response.loc[index, 'surface_reelle_bati']) and not pd.isnull(response.loc[index, 'valeur_fonciere']) and (row['type_local'] == 'Maison'):
				maison_response.append(row)

			if not pd.isnull(response.loc[index, 'surface_reelle_bati']) and not pd.isnull(response.loc[index, 'valeur_fonciere']) and (row['type_local'] == 'Appartement'):
				appartement_response.append(row)

		if len(maison_response) > len(appartement_response):
			type_local_response = maison_response
		else:
			type_local_response = appartement_response

		valeur = surface = mutations_nb = 0
		for res in type_local_response:
			valeur += int(res['valeur_fonciere'])
			mutations_nb += 1

			if not math.isnan(res['surface_terrain']):
				surface += int(res['surface_reelle_bati']) + int(res['surface_terrain'])

			else:
				surface += int(res['surface_reelle_bati'])

		if valeur > 0 and surface > 0:
			return {'m2': valeur/surface, 'prix_moy' : valeur/mutations_nb, 'surface_moy': surface/mutations_nb}    


	def get_dvf(self, dep):
		"""
		"""
		communes = self.get_communes(dep)
		values = dict()
		error = False

		page = requests.get('https://cadastre.data.gouv.fr/data/etalab-dvf/latest/csv/2019/communes/{}/'.format(dep))
		soup = BeautifulSoup(page.text, 'html.parser')
		scrap = soup.findAll('a', href = re.compile('\.csv$'))
		communes_scrap = [file.getText().split(".")[0] for file in scrap]
		
		cpt_codes = 0

		for com in communes_scrap:
			error = False
			print("Dep", dep, communes_scrap.index(com)+1, len(communes_scrap), end='\r')

			url_csv = 'https://cadastre.data.gouv.fr/data/etalab-dvf/latest/csv/2019/communes/{}/{}.csv'.format(dep, com)
			df = pd.read_csv(url_csv)

			try:
				code_postal = df['code_postal'].iloc[0]
				code_insee = df['code_commune'].iloc[0]

				while np.isnan(code_postal):
					i += 1
					code_postal = df['code_postal'].iloc[i]

				i = 0

				while np.isnan(code_insee):
					i += 1
				code_insee = df['code_commune'].iloc[i]

				code_postal = str(int(code_postal))
				code_insee = str(int(code_insee))

			except:
				error = True

			if not error:
				valeur_local = self.get_valeur_local(df)

				if valeur_local:
					if code_insee not in communes.keys():
						for commune_code in communes.keys():
							commune = communes[commune_code]

							if code_postal in commune['properties']['codesPostaux']:
								com = commune['properties']['code']
								valeurs = {'geometry': commune['geometry']}

								if com in values.keys():
									values[com]['valeur_locaux']['m2'] += valeur_local['m2']

									values[com]['commune'] = commune['properties']['nom']
								else:
									valeurs = {'geometry': commune['geometry']}

									valeurs['valeur_locaux'] = valeur_local
									values[com] = valeurs
									values[com]['commune'] = commune['properties']['nom']

								commune['properties']['codesPostaux'].remove(code_postal)
								cpt_codes += 1

								if not len(commune['properties']['codesPostaux']):
									values[com]['valeur_locaux']['m2'] = values[com]['valeur_locaux']['m2']/cpt_codes
									cpt_codes = 0

					
					else:
						valeurs = {'geometry': communes[code_insee]['geometry']}
						valeurs['valeur_locaux'] = valeur_local
						values[com] = valeurs
						values[com]['commune'] = communes[code_insee]['properties']['nom']

		return values



		# for commune in communes:
		#   print("Dep", dep, communes.index(commune), len(communes), end='\r')
		#   valeurs = {'geometry': commune['geometry']}
		#   com = commune['properties']['code']

		#   url_csv = 'https://cadastre.data.gouv.fr/data/etalab-dvf/latest/csv/2019/communes/{}/{}.csv'.format(dep, com)

		#   try:
		#       df = pd.read_csv(url_csv)
		#       error = False
		#   except:
		#       error = True#File not found

		#   if not error:
		#       valeur_local = self.get_valeur_local(df)
		#       if valeur_local:
		#           valeurs['valeur_locaux'] = valeur_local
		#           values[com] = valeurs
		#           values[com]['commune'] = commune['properties']['nom']



	def get_color(self, feature, data):
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
		:param text list: data to display on the map
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
			folium.Popup("Commune : " + str(temp_feature['commune']) + "\n Prix m2 : " + str(int(map_dict[temp_feature['code_com']])) + "€").add_to(temp_layer)

			temp_layer.add_to(self.osm_map)
		LinearColormap(['white','red'], index=[val_min, 100*np.log(val_max)], vmin = val_min, vmax = 100*np.log(val_max)).add_to(self.osm_map)

		# folium.Choropleth(
		#    geo_data = geojson_data, # geoJSON file
		#    name = 'choropleth',
		#    data = data, # Pandas dataframe
		#    columns=['code_com', 'm2'], # key and value of interest from the dataframe
		#    key_on='feature.code_com', # key to link the json file and the dataframe
		#    fill_color='blues', # colormap
		#    fill_opacity=0,
		#    line_opacity=0.2,
		#    legend_name='Evolution prix m2'
		# ).add_to(self.osm_map)

	def create_map_dep(self, dep):
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
			feature = {'type' : 'Feature', 'commune': dvf_dep[com]['commune'], 'code_com': com, 'properties': {'name': com}}
			feature['geometry'] = dvf_dep[com]['geometry']

			geojson_collection['features'].append(feature)

			data['code_com'].append(com)
			data['m2'].append(dvf_dep[com]['valeur_locaux']['m2'])


		df = pd.DataFrame (data, columns = ['code_com', 'm2'])

		self.data = df

		self.add_layers(geojson_collection, df)

		parent_dir = Path(os.getcwd()).parent
		file = Path.joinpath(parent_dir, "static", "maps", "{}.html".format(dep))

		self.osm_map.save(str(file))


m = map()
deps = m.get_dep()
for dep in deps:
	print((deps.index(dep)/len(deps))*100, ' %', '\n', end='\r')
	m.create_map_dep(dep)

#m.create_map_dep(62)



