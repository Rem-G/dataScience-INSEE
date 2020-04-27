import requests
import json

class DVF():
	def __init__(self):
		self.code_insee = None

	def set_code_insee(self, code_insee):
		self.code_insee = code_insee

	def auth_api(self, url):
		token_auth = ''

		headers={'Authorization': token_auth}
		response = requests.get(url, headers=headers)
		return requests.get(url)

	def get_dvf(self, type_local, commerce):
		"""
		"""
		if commerce:
			url = "http://api.cquest.org/dvf?code_commune={}&code_type_local={}".format(self.code_insee, 4)
		else:
			url = "http://api.cquest.org/dvf?code_commune={}&type_local={}".format(self.code_insee, type_local)
		return self.auth_api(url).json()

	def get_valeur_local(self, type_local, terrain=False, commerce=False):
		response = self.get_dvf(type_local, commerce)
		type_local_response = list()

		for x in response['resultats']:
			if x['surface_relle_bati'] and x['valeur_fonciere']:
				type_local_response.append(x)

		valeur = surface = mutations_nb = 0
		for res in type_local_response:

			if res['surface_terrain'] and terrain:
				valeur += int(res['valeur_fonciere'])
				surface += int(res['surface_relle_bati']) + int(res['surface_terrain'])
				mutations_nb+=1

			elif not terrain and not res['surface_terrain']:
				valeur += int(res['valeur_fonciere'])
				surface += int(res['surface_relle_bati'])
				mutations_nb+=1

		return {'m2': valeur/surface, 'prix_moy' : valeur/mutations_nb, 'surface_moy': surface/mutations_nb}		


api = DVF()
api.set_code_insee('74010')

print('m2 maison terrain + bati', api.get_valeur_local('Maison', terrain=True))
print('m2 maison bati', api.get_valeur_local('Maison'))
print('m2 appartement terrain + bati', api.get_valeur_local('Appartement', terrain=True))
print('m2 appartement bati', api.get_valeur_local('Appartement'))

print('m2 commerce terrain + bati', api.get_valeur_local('Commerce', terrain=True, commerce=True))
print('m2 commerce bati', api.get_valeur_local('Commerce', commerce=True))




