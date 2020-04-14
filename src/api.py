import requests
import json

class Api():

	def auth_api(self, url):
		token_auth = ''

		headers={'Authorization': token_auth}
		response = requests.get(url, headers=headers)
		return requests.get(url)

	def get_dvf(self, code_insee):
		"""
		"""
		url = "http://api.cquest.org/dvf?code_commune={}".format(code_insee)
		print(url)
		response = self.auth_api(url).json()
		response = response["resultats"]

		valeur = surface = cpt = 0

		for res in response:
			cpt += 1
			try:
				valeur += int(res['valeur_fonciere'])
				surface += int(res['surface_terrain'])
			except:
				try:
					valeur += int(res['valeur_fonciere'])
					surface += int(res['surface_relle_bati'])
				except:
						print(res)

		print("Prix m2 ", valeur/surface)



Api().get_dvf('74010')

