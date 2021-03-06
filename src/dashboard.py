import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc

import pandas as pd
import plotly.graph_objs as go
from pathlib import Path
import os
import flask

from statistic import *
from data_manage import *

DataManage().manage(dbreset = False, mapsreset = False)

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.DARKLY])
app.title = 'Dash 3 en 1'
app.config['suppress_callback_exceptions']=True

server = app.server

DEFAULT_PLOTLY_COLORS=['rgb(31, 119, 180)', 'rgb(255, 127, 14)',
					   'rgb(44, 160, 44)', 'rgb(214, 39, 40)',
					   'rgb(148, 103, 189)', 'rgb(140, 86, 75)',
					   'rgb(227, 119, 194)', 'rgb(127, 127, 127)',
					   'rgb(188, 189, 34)', 'rgb(23, 190, 207)']

#Intégration des static files
parent_dir = Path(os.getcwd()).parent
STATIC_PATH = Path.joinpath(parent_dir, "static")

s = Statistic()
years = s.get_years()

years_options = [{'label': 'Multi millésimes', 'value': '/'}]
for year in years:
	years_options.append({'label': year, 'value': str(year)})

@app.server.route('/static/<resource>')
def serve_static(resource):
	return flask.send_from_directory(STATIC_PATH, resource)

def get_options():
	return {dep: [com[0] for com in s.get_communes(dep)] for dep in s.get_deps()}

all_options = get_options()

select_dep = [
				dbc.Label('Départements :', style={'font-size':'15px'}),
				dcc.Dropdown(
					id = 'departements',
					options=[{'label': s.get_dep_name(dep)+" ({})".format(dep), 'value': dep} for dep in all_options.keys()],
					multi=True,
					value=['74'],
					style={'backgroundColor': 'transparent', 'font-size': '15px', 'border-radius':'0.5em'},
					placeholder='Départements',
				)
			]

select_com = [
				dbc.Label('Communes :', style={'font-size':'15px'}),
				dcc.Dropdown(
					id = 'communes',
					multi=True,
					value=['Annecy'],
					style={'backgroundColor': 'transparent', 'font-size': '15px', 'border-radius':'0.5em'},
					placeholder='Communes',
				)
			]

select_year = [
				dbc.Label('Millésimes :', style={'font-size':'15px'}),
				dcc.Dropdown(
					id = 'years',
					multi=False,
					options=years_options,
					value='/',
					style={'backgroundColor': 'transparent', 'font-size': '15px', 'border-radius':'0.5em'},
					placeholder='Millésimes',
					className = 'years-dropdown',
				)
			]                

navbar = dbc.Navbar([
				# Use row and col to control vertical alignment of logo / brand
				dbc.Row(
					[
						dbc.Col(html.Img(src='/static/logo_polytech.png', height="50px")),
						dbc.Col(dbc.NavbarBrand("Dash 3 en 1", className="col-1")),
						dbc.Col(select_dep, className="col-2 ml-4"),
						dbc.Col(select_com, className="col-2 ml-4"),
						dbc.Col(select_year, className="col-2 ml-4"),
					],
					align='center',
					className="flex-nowrap",
					style={'width': '100%'}
				),
		], sticky='d', color="rgba(48, 48, 48, 1)")

# card colors = info | success | warning | danger | rose.

com_cards = dbc.Card([
				dbc.Row([
					dbc.Col(
						dbc.Card([
							html.Span("Commune :",
									className="card-text"),
							html.Span("NUMBER", id = "card1_nom", style={'font-weight': 'bold', 'font-size': 18, 'color': 'rgba(0, 173, 240, 0.8)'}),
							html.Span("Code INSEE :",
									className="card-text"),
							html.Span("NUMBER", id = "card1_insee", style={'font-weight': 'bold', 'font-size': 18, 'color': 'rgba(0, 173, 240, 0.8)'}),
							html.Span("Codes postaux :",
									className="card-text"),
							html.Span("NUMBER", id="card1_postal", style={'font-weight': 'bold', 'font-size': 18, 'color': 'rgba(0, 173, 240, 0.8)'}),
							html.Span("Superficie (km²) :",
									className="card-text"),
							html.Span("NUMBER", id="card1_superficie", style={'font-weight': 'bold', 'font-size': 18, 'color': 'rgba(0, 173, 240, 0.8)'}), 
						], inverse=True, style={'border-radius':'0.5em', 'margin-top' : '0px',
												'text-align' : 'center',
												'background' : 'rgba(48, 48, 48, 1)',
												'border-color': 'lightgrey'}						
						)
					),
					dbc.Col(
						dbc.Card([
							html.Span("Tranche d'âge la plus représentée :", className='card-text'),
							html.Span("NUMBER", id = "card2_group", style={'font-weight': 'bold', 'font-size': 18, 'color': 'rgba(0, 173, 240, 0.8)'}),
							html.Span("Nombre de personnes dans cette tranche d'âge :",
									className="card-text"),
							html.Span("NUMBER", id = "card2_pop", style={'font-weight': 'bold', 'font-size': 18, 'color': 'rgba(0, 173, 240, 0.8)'})
						], inverse=True, style={'border-radius':'0.5em', 'margin-top' : '0px',
												'text-align' : 'center',
												'background' : 'rgba(48, 48, 48, 1)',
												'border-color': 'lightgrey'}
						)
					),
					dbc.Col(
						dbc.Card([
							html.Span("Population :",
									className="card-text"),
							html.Span("NUMBER", id = "card3_pop", style={'font-weight': 'bold', 'font-size': 18, 'color': 'rgba(0, 173, 240, 0.8)'}),
							html.Span("Densité de population (hab/km²) :", className="card-text"),
							html.Span("NUMBER", id = "card3_densite", style={'font-weight': 'bold', 'font-size': 18, 'color': 'rgba(0, 173, 240, 0.8)'})
						], inverse=True, style={'border-radius': '0.5em',
												'text-align' : 'center',
												'background' : 'rgba(48, 48, 48, 1)',
												'border-color': 'lightgrey'}						
						)
					)
				], align='center'),
				dbc.Row([
					dbc.Col(
						dbc.Card([
							html.Span(
								"Nombre de commerces alimentaires :",
								className="card-text"),
							html.Span("NUMBER", id="card4_shop_food", style={'font-weight': 'bold', 'font-size': 18, 'color': 'rgba(0, 173, 240, 0.8)'}),
							html.Span("Nombre de commerces non alimentaires :",
								className="card-text"),
							html.Span("NUMBER", id = "card4_shop", style={'font-weight': 'bold', 'font-size': 18, 'color': 'rgba(0, 173, 240, 0.8)'}),

						], inverse=True, style={'border-radius':'0.5em',
												'text-align' : 'center',
												'background' : 'rgba(48, 48, 48, 1)',
												'border-color': 'lightgrey'}						
						)
					),
					dbc.Col(
						dbc.Card([
							html.Span("Taux de chômage :",
									className="card-text"),
							html.Span("NUMBER", id = "card5_taux", style={'font-weight': 'bold', 'font-size': 18, 'color': 'rgba(0, 173, 240, 0.8)'}),
							html.Span("soit", className="card-text"),
							html.Span("NUMBER", id="card5_nb", style={'font-weight': 'bold', 'font-size': 18, 'color': 'rgba(0, 173, 240, 0.8)'}),
							html.Span("personnes"),
						], inverse=True, style={'border-radius':'0.5em',
												'text-align' : 'center',
												'background' : 'rgba(48, 48, 48, 1)',
												'border-color': 'lightgrey'}						
						)
					)
				], align='center')
			], style={'border-radius':'0.5em', 'border-color': 'transparent'}, color='transparent')

body_multi = [dbc.Row([
				dbc.Col(
					dbc.Card(
						dcc.Graph(id='graph-evolution-pop'), color="light", outline=True, style={'border-radius':'0.5em'})
				, width=4, align="center"),

				dbc.Col(
					dbc.Card(
						dcc.Graph(id='graph-evolution-soc-pro'), color="light", outline=True, style={'border-radius':'0.5em'})
				, width=8, align="center")

			], style={'margin-bottom': '5px', 'margin-left': '5px', 'margin-right': '5px'}),

			html.Div(id='graph-ages', style={'display': 'none'})
			]

body_year = dbc.Row([
				dbc.Col(
					dbc.Card(
						dcc.Graph(id='graph-evolution-pop'), color="light", outline=True, style={'border-radius':'0.5em'}
					)
				, width=3, align="center"),

				dbc.Col(
					dbc.Card(
						dcc.Graph(id='graph-evolution-soc-pro'), color="light", outline=True, style={'border-radius':'0.5em'})
				, width=4, align="center"),

				dbc.Col(
					dbc.Card(
						dcc.Graph(id='graph-ages'), color="light", outline=True, style={'border-radius':'0.5em'})
				, width=5, align="center"),

		], style={'margin-bottom': '5px', 'margin-left': '5px', 'margin-right': '5px'})

modal = dbc.Modal(
			[
				dbc.ModalHeader("Dash 3 en 1 - Utilisation"),
				dbc.ModalBody([
					html.P("Ce dashboard propose des indicateurs à partir de différentes données sur une ou plusieurs communes de France métropolitaine et d'Outre-mer."),
					html.P("Deux modes disponibles :"),
					html.P("- Multi-millésimes : affiche les indicateurs de chaque commune ainsi que la somme de ces derniers"),
					html.P("- Annuel : affiche des indicateurs plus précis sur une commune à une date donnée"),
					html.P("Pour chaque graphique les courbes peuvent être activées ou désactivées en cliquant sur leur nom dans la légende."),
					html.P("La carte proposée à partir des données DVF est cliquable, elle permet d'obtenir la valeur foncière moyenne d'un m2 de logement dans une commune mais aussi de comparer cette valeur avec les autres communes du département."),
					html.P("Sources : Insee, DVF, geo.api.gouv.fr, cadastre.data.gouv.fr")

				]),
				dbc.ModalFooter(
					dbc.Button(
						"Fermer", id="close-centered", className="ml-auto"
					)
				),
			],
			id="modal",
			centered=True,
		)

modal_map = dbc.Modal(
			[
				dbc.ModalHeader("Valeur foncière logement - Donnée DVF"),
				dbc.ModalBody([
						html.Div(id='modal_map_div')
				]),
				dbc.ModalFooter(
					dbc.Button(
						"Fermer", id="close-centered-map", className="ml-auto"
					)
				),
			],
			id="modal_map",
			centered=True,
			size='xl',
		)

app.layout = html.Div([
		modal,
		modal_map,
		navbar,
		dbc.Container([
			dbc.Card([
				dbc.Row([
					dbc.Col(
						html.Div(
							com_cards,
							style={'overflow': 'auto', 'max-height': '370px'},
						),
						style={'width': '100%'},
						align = 'center'
					),
					dbc.Col([
						html.P(["Valeur foncière logement - Donnée DVF ", dbc.Button('Agrandir', style={'height': 24, 'font-size': 10, 'background-color': 'rgba(0, 173, 240, 0.8)'}, id="p_map")], style={'text-align': 'center', 'height': 10}),
						html.Div(id='map')])
				], style={'margin-left': '5px', 'margin-right': '5px'}),

				html.Div(id='page-content')
			], style={'background-color': 'transparent', 'border-color': 'white'})
		], fluid=True)
	])

########################################################
#################### CALLBACKS #########################
########################################################

########################################################
#################### DISPLAY PAGE ######################
########################################################

@app.callback(dash.dependencies.Output('page-content', 'children'),
			[
				dash.dependencies.Input('years', 'value')
			])

def display_page(year):
	if year == '/':
		return body_multi

	elif int(year) in years:
		return body_year

########################################################
#################### COMMUNES OPTIONS ##################
########################################################

@app.callback(dash.dependencies.Output('communes', 'options'),
			[	
				dash.dependencies.Input('departements', 'value')
			])

def communes_options(selected_dep):
	'''
	Affichage des communes disponibles en fonction du département sélectionné
	'''
	communes = list()
	deps = [all_options[dep] for dep in selected_dep]
	for dep in deps:
		for com in dep:
			communes.append({'label': com, 'value': com})
	return communes


########################################################
#################### MODALS CALLBACKS ##################
########################################################

@app.callback([
				dash.dependencies.Output("modal", "is_open")
			],
			[
				dash.dependencies.Input("close-centered", "n_clicks")
			],
			[
				dash.dependencies.State("modal", "is_open")
			])
def display_modal(n, is_open):
	if n and is_open:
		return [False]
	return [True]

@app.callback(dash.dependencies.Output("modal_map", "is_open"),
			[
				dash.dependencies.Input("close-centered-map", "n_clicks"),
				dash.dependencies.Input("p_map", "n_clicks")
			],
			[
				dash.dependencies.State("modal_map", "is_open")
			])
def update_modal_map(n, map_click, is_open):
	if n and is_open:
		return False

	elif map_click:
		return True

########################################################
#################### MAPS UPDATE #######################
########################################################

@app.callback([
				dash.dependencies.Output('map', 'children')
			],
			[
				dash.dependencies.Input('departements', 'value')
			])

def update_map(selector):
	if len(selector):
		if Path(str(Path.joinpath(STATIC_PATH, 'maps', selector[0])) + '.html').is_file():
			return [html.Iframe(srcDoc = open(str(Path.joinpath(STATIC_PATH, 'maps', selector[0])) + '.html', 'r', encoding='utf-8').read(), width='100%', height='370', style={'border-radius':'0.5em'})]
		else:
			return [html.Iframe(srcDoc = open(str(Path.joinpath(STATIC_PATH, 'nodata')) + '.html', 'r', encoding='utf-8').read(), width='100%', height='370', style={'border-radius':'0.5em'})]

@app.callback([
				dash.dependencies.Output('modal_map_div', 'children')
			],
			[
				dash.dependencies.Input('departements', 'value')
			])

def update_map_modal(selector):
	if len(selector):
		if Path(str(Path.joinpath(STATIC_PATH, 'maps', selector[0])) + '.html').is_file():
			return [html.Iframe(srcDoc = open(str(Path.joinpath(STATIC_PATH, 'maps', selector[0])) + '.html', 'r', encoding='utf-8').read(), width='100%', height='600', style={'border-radius':'0.5em'})]
		else:
			return [html.Iframe(srcDoc = open(str(Path.joinpath(STATIC_PATH, 'nodata')) + '.html', 'r', encoding='utf-8').read(), width='100%', height='600', style={'border-radius':'0.5em'})]

########################################################
################ COMMUNE INDICATOR CARDS ###############
########################################################

@app.callback([
				dash.dependencies.Output('card1_nom', 'children'),
				dash.dependencies.Output('card1_insee', 'children'),
				dash.dependencies.Output('card1_postal', 'children'),
				dash.dependencies.Output('card1_superficie', 'children'),
				dash.dependencies.Output('card3_pop', 'children'),
				dash.dependencies.Output('card3_densite', 'children'),
			],
			[
				dash.dependencies.Input('communes', 'value'),
				dash.dependencies.Input('departements', 'value')
			 ])

def stats_commune(com, dep):

	city = com[0].lower()

	res = s.com_info(city, dep[0])

	nom = res['nom']
	code_postal = res['code_postal']
	code_insee = res['code_insee']
	superficie = res['superficie']
	pop = res['pop']
	densite = res['densite']

	return [nom, code_insee, code_postal, superficie, pop, densite]

@app.callback([
				dash.dependencies.Output('card2_group', 'children'),
				dash.dependencies.Output('card2_pop', 'children'),
			],
			[
			  dash.dependencies.Input('years', 'value'),
			  dash.dependencies.Input('communes', 'value')
			 ])

def stats_age_group(year, com):
	if(year == '/'):
		year = 2016

	age_group = s.get_largest_age_group(int(year), com[0])

	most_represented_age_group = [age_group[0][1]," - ", age_group[0][2], "ans"]
	population_in_most_represented_age_group = age_group[0][0]

	return [most_represented_age_group, population_in_most_represented_age_group]

@app.callback([
				dash.dependencies.Output('card4_shop', 'children'),
				dash.dependencies.Output('card4_shop_food', 'children'),
			],
			[
			  dash.dependencies.Input('communes', 'value'),
			  dash.dependencies.Input('departements', 'value')
			 ])

def stats_commerce(com, dep):
	if 'arrondissement' in com[0].lower():
		city = com[0].split(" ")[0]
	else:
		city = com[0]

	res = s.commerces_com(com[0], dep[0])

	shop = res['other']
	shop_food = res['food']
	return [shop, shop_food]

@app.callback([
				dash.dependencies.Output('card5_taux', 'children'),
				dash.dependencies.Output('card5_nb', 'children')
			],
			[
				dash.dependencies.Input('years', 'value'),
				dash.dependencies.Input('communes', 'value')
			])

def stats_chomage(year, com):
	if(year == '/'):
		year = 2016

	city = com[0]

	chomeur = s.get_chomeur(city, year)

	if chomeur:
		actif = s.get_actif(city, year) - chomeur
		taux = round((chomeur / actif) * 100, 2)
		taux = str(taux) + "%"

		return [taux, str(int(chomeur))]
	return [None, None]

########################################################
#################### UPDATE GRAPHES ####################
########################################################

@app.callback([
		dash.dependencies.Output('graph-evolution-pop', 'figure'),
		dash.dependencies.Output('graph-evolution-soc-pro', 'figure'),
		dash.dependencies.Output('graph-ages', 'figure')
	],
	[
		dash.dependencies.Input('communes', 'value'),
		dash.dependencies.Input('years', 'value')
	])
def update_graphes(commune, year):
	if year == '/':
		return [update_graph_evolution_pop(commune), update_graph_evolution_soc_pro(commune), None]

	elif int(year) in years:
		return [update_graph_evolution_pop_year(commune, year), update_graph_evolution_soc_pro_year(commune, year), update_graph_ages(commune, year)]


########################################################
################# GRAPHES FUNCTIONS ####################
########################################################

########################################################
#################### MULTI GRAPHES #####################
########################################################

def update_graph_evolution_pop(selected_commune):
	traces = list()
	all_period = dict()

	for commune in selected_commune:
		population_years = s.get_pop_all_period(commune)

		x_years = list()
		y_pop = list()
		y_pop_men = list()
		y_pop_women = list()

		for year, pop in population_years.items():
			x_years.append(int(year))

			y_pop.append(int(pop[0]))
			y_pop_men.append(int(pop[1]))
			y_pop_women.append(int(pop[2]))

			if year in all_period.keys():
				all_period[year] += int(pop[0])+int(pop[1])+int(pop[2])
			else:
				all_period[year] = int(pop[0])+int(pop[1])+int(pop[2])

		traces.append(dict(
			fill='tozeroy',
			x = x_years,
			y = y_pop,
			name = commune+' Total',
			marker = dict(color = 'rgba(55, 83, 109, 1)'),
			)
		)

		traces.append(dict(
			fill='tozeroy',
			x = x_years,
			y = y_pop_men,
			name = commune+' Hommes',
			marker = dict(color = DEFAULT_PLOTLY_COLORS[3]),
			visible = 'legendonly'
			)
		)

		traces.append(dict(
			fill='tozeroy',
			x = x_years,
			y = y_pop_women,
			name = commune+' Femmes',
			marker = dict(color = DEFAULT_PLOTLY_COLORS[0]),
			visible = 'legendonly'
			)
		)

	all_period_years = list(all_period.keys())
	all_period_pop = list(all_period.values())
	legend_title = selected_commune[0]

	if len(selected_commune) > 1:
		legend_title = ", ".join(selected_commune[0:2])+"..."
		traces.append(dict(
			fill='tozeroy',
			x = all_period_years,
			y = all_period_pop,
			name = legend_title,
			marker = dict(color = DEFAULT_PLOTLY_COLORS[1]),
			)
		)

	figure =  {
		'data': traces,
		'layout': dict(
			margin={'t': 40, 'b': 0, 'l': 0, 'r': 0},
			title = "Evolution de la population à {} de {} à {}".format(legend_title, min(years), max(years)),
			xaxis = {'gridcolor' : 'rgba(238, 238, 238, 0)'},
			yaxis = {'gridcolor' : 'rgba(238, 238, 238, 0)'},
			hovermode = 'closest',
			paper_bgcolor =  'transparent',
			plot_bgcolor = 'transparent',
			font = {'color': 'white', 'size': 10},
			legend = dict(orientation="h", y=-0.2),
			height = 300,
		),
	}

	return figure

def update_graph_evolution_soc_pro(selected_commune):
	traces = list()
	n = 0

	for commune in selected_commune:
		categories_soc_pro_commune_years = s.categories_soc_pro_commune(commune)
		x_years = categories_soc_pro_commune_years['years']
		y_pop = dict()
		y_pop_unemployment = dict()

		for key, value in categories_soc_pro_commune_years['employment'].items():
			if key.split('_Actifs_ayant_un_emploi')[0] in y_pop.keys():
				y_pop[key.split('_Actifs_ayant_un_emploi')[0]].append(int(value))

			else:
				y_pop[key.split('_Actifs_ayant_un_emploi')[0]] = [int(value)]

		for key, value in y_pop.items():
			if n >= len(DEFAULT_PLOTLY_COLORS):
				n = 0

			traces.append(dict(
				x = x_years,
				y = value,
				name = commune+' '+' '.join(key.split("_")),
				marker = dict(color = DEFAULT_PLOTLY_COLORS[n]),
				)
			)

			n += 1

		for key, value in categories_soc_pro_commune_years['unemployment'].items():
			if key.split("RP")[1] in y_pop_unemployment.keys():
				y_pop_unemployment[key.split("RP")[1]] += int(value)
			else:
				y_pop_unemployment[key.split("RP")[1]] = int(value)

		traces.append(dict(
			x = x_years,
			y = [value for key, value in y_pop_unemployment.items()],
			name = commune+' Chomeurs',
			marker = dict(color = DEFAULT_PLOTLY_COLORS[n]),
			)
		)

	legend_title = selected_commune[0]

	figure =  {
		'data': traces,
		'layout': dict(
			title = "Evolution des catégories socio-professionnelles à {} de {} à {}".format(legend_title, min(years), max(years)),
			xaxis = {'gridcolor' : 'rgba(238, 238, 238, 0)'},
			yaxis = {'title': 'Population', 'gridcolor' : 'rgba(238, 238, 238, 0)'},
			hovermode = 'closest',
			margin={'t': 40, 'b': 0, 'l': 0, 'r': 0},
			font = {'color': 'white', 'size': 10},
			paper_bgcolor =  'transparent',
			plot_bgcolor = 'transparent',
			legend = dict(orientation="h", y=-0.2),
			height = 300,
		),
	}

	return figure

########################################################
#################### YEAR GRAPHES ######################
########################################################

def update_graph_evolution_pop_year(selected_commune, year):
	population_years = s.get_pop_all_period(selected_commune[0])

	y_pop_men = int(population_years[str(year)][1])
	y_pop_women = int(population_years[str(year)][2])

	traces = [go.Pie(labels=['Hommes', 'Femmes'], values=[y_pop_men, y_pop_women], marker=dict(colors=[DEFAULT_PLOTLY_COLORS[3], 'rgba(55, 83, 109, 1)']))]

	figure =  {
		'data': traces,
		'layout': dict(
			margin={'t': 60, 'b': 0, 'l': 0, 'r': 0},
			title = "Répartition de la population à<br>{} en {}".format(selected_commune[0], year),
			hovermode = 'closest',
			paper_bgcolor =  'transparent',
			plot_bgcolor = 'transparent',
			font = {'color': 'white', 'size': 10},
			legend = dict(orientation="h", y=-0.1),
			height = 300,
		),
	}

	return figure

def update_graph_evolution_soc_pro_year(selected_commune, year):
	commune = selected_commune[0]

	categories_soc_pro_commune_year = s.categories_soc_pro_commune(commune)
	traces = list()
	y_pop_unemployment = 0
	n = 0

	for key, value in categories_soc_pro_commune_year['employment'].items():
		if str(year) in key:
			if n >= len(DEFAULT_PLOTLY_COLORS):
				n = 0

			traces.append(dict(
				y = [int(value)],
				name = ' '.join(key.split('_Actifs_ayant_un_emploi')[0].split("_")),
				type = 'bar',
				marker = dict(color = DEFAULT_PLOTLY_COLORS[n]),
				)
			)
			n += 1

	for key, value in categories_soc_pro_commune_year['unemployment'].items():
		if str(year) in key:
			y_pop_unemployment+=int(value)

	traces.append(dict(
		y = [y_pop_unemployment],
		name = 'Chomeurs',
		type = 'bar',
		marker = dict(color = DEFAULT_PLOTLY_COLORS[n]),
		)
	)

	figure =  {
		'data': traces,
		'layout': dict(
			margin={'t': 40, 'b': 0, 'l': 0, 'r': 0},
			title = "Catégories socio-professionnelles à {} en {}".format(selected_commune[0], year),
			xaxis = {'gridcolor' : 'rgba(238, 238, 238, 0)', 'visible': False},
			yaxis = {'title': 'Population', 'gridcolor' : 'rgba(238, 238, 238, 0)'},
			hovermode = 'closest',
			paper_bgcolor =  'transparent',
			plot_bgcolor = 'transparent',
			font = {'color': 'white', 'size': 10},
			legend = dict(orientation="h", y=-0.2),
			height = 300,
		),
	}

	return figure

def update_graph_ages(selected_commune, year):
	commune = selected_commune[0]

	ages = s.pop_stats_all_period(year, commune)

	traces = list()

	n = 0
	for key, value in ages.items():
		key_split = key.split("_")[:len(key.split("_"))-2]
		label = ' '.join(key_split[1:4])

		if 'hommes' in key.lower():
			traces.append(dict(
				x = [n],
				y = [ages[key]],
				name = 'H. '+label,
				type = 'bar',
				marker = dict(color=DEFAULT_PLOTLY_COLORS[3]),
				)
			)

		elif 'femmes' in key.lower():
			traces.append(dict(
				x = [n],
				y = [ages[key]],
				name = 'F. '+label,
				type = 'bar',
				marker = dict(color='rgba(55, 83, 109, 1)'),
				)
			)
			n += 5

	figure =  {
		'data': traces,
		'layout': dict(
			margin={'t': 40, 'b': 20, 'l': 12, 'r': 0},
			title = "Répartition de la population par tranches d'âge à {} en {}".format(selected_commune[0], year),
			xaxis = {'title': '', 'gridcolor' : 'rgba(238, 238, 238, 0)', 'tickmode' : 'linear', 'dtick': 5},
			yaxis = {'title': 'Population', 'gridcolor' : 'rgba(238, 238, 238, 0)', 'showticklabels': False},
			hovermode = 'closest',
			paper_bgcolor =  'transparent',
			plot_bgcolor = 'transparent',
			font = {'color': 'white', 'size': 10},
			legend = dict(orientation="h", y=-0.2),
			height = 300,
			showlegend = False,
			barmode='stack',
		),
	}

	return figure

if __name__ == '__main__':
	app.run_server(debug=False)
