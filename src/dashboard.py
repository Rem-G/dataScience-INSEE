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

import main

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.DARKLY])
app.title = 'Insee Dashboard'
app.config['suppress_callback_exceptions']=True

server = app.server

DEFAULT_PLOTLY_COLORS=['rgb(31, 119, 180)', 'rgb(255, 127, 14)',
                       'rgb(44, 160, 44)', 'rgb(214, 39, 40)',
                       'rgb(148, 103, 189)', 'rgb(140, 86, 75)',
                       'rgb(227, 119, 194)', 'rgb(127, 127, 127)',
                       'rgb(188, 189, 34)', 'rgb(23, 190, 207)']


#tranches âge la plus représentée pour une année donnée (h, f, m), répartition pop catégorie socio-prof, nombre habitants, commerces

#Intégration des static files
parent_dir = Path(os.getcwd()).parent
STATIC_PATH = Path.joinpath(parent_dir, "static")
s = Statistic()
years = s.get_years()

years_options = [{'label': 'Multi millésime', 'value': '/'}]
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
					style={'backgroundColor': 'rgba(42,42,42, 0.1)', 'color':'grey', 'font-size': '15px', 'border-radius':'0.5em'},
					placeholder='Départements',
				)
			]

select_com = [
				dbc.Label('Communes :', style={'font-size':'15px'}),
				dcc.Dropdown(
					id = 'communes',
					multi=True,
					value=['Annecy'],
					style={'backgroundColor': 'rgba(42,42,42, 0.1)', 'color':'grey', 'font-size': '15px', 'border-radius':'0.5em'},
					placeholder='Communes'   
				)
			]

select_year = [
				dbc.Label('Années :', style={'font-size':'15px'}),
				dcc.Dropdown(
					id = 'years',
					multi=False,
					options=years_options,
					value='/',
					style={'backgroundColor': 'rgba(42,42,42, 0.1)', 'color':'grey', 'font-size': '15px', 'border-radius':'0.5em'},
					placeholder='Années'   
				)]                

navbar = dbc.Navbar([
				# Use row and col to control vertical alignment of logo / brand
				dbc.Row(
					[
						dbc.Col(html.Img(src='/static/logo_polytech.png', height="50px")),
						dbc.Col(dbc.NavbarBrand("Insee Dashboard", className="col-1")),
						dbc.Col(select_dep, className="col-2 ml-4"),
						dbc.Col(select_com, className="col-2 ml-4"),
						dbc.Col(select_year, className="col-2 ml-4"),
					],
					align='center',
    				className="flex-nowrap",#ml-auto : margin-left auto, mt-3 : $spacer margin top mt-md-0
    				style={'width': '100%'}
				),
		], sticky='top', color="#484848", style={'margin-bottom': '5px'})

com_cards = dbc.Card([
				dbc.Row([
					dbc.Col(
						dbc.Card(
							html.P("TEST")
						)
					),
					dbc.Col(
						dbc.Card(
							html.P("TEST")
						)
					)
				]),
				dbc.Row([
					dbc.Col(
						dbc.Card(
							html.P("TEST")
						)
					),
					dbc.Col(
						dbc.Card(
							html.P("TEST")
						)
					)
				]),
				dbc.Row([
					dbc.Col(
						dbc.Card(
							html.P("TEST")
						)
					),
					dbc.Col(
						dbc.Card(
							html.P("TEST")
						)
					)
				]),
				dbc.Row([
					dbc.Col(
						dbc.Card(
							html.P("TEST")
						)
					),
					dbc.Col(
						dbc.Card(
							html.P("TEST")
						)
					)
				]),
				dbc.Row([
					dbc.Col(
						dbc.Card(
							html.P("TEST")
						)
					),
					dbc.Col(
						dbc.Card(
							html.P("TEST")
						)
					)
				]),
				dbc.Row([
					dbc.Col(
						dbc.Card(
							html.P("TEST")
						)
					),
					dbc.Col(
						dbc.Card(
							html.P("TEST")
						)
					)
				]),
				dbc.Row([
					dbc.Col(
						dbc.Card(
							html.P("TEST")
						)
					),
					dbc.Col(
						dbc.Card(
							html.P("TEST")
						)
					)
				]),
				dbc.Row([
					dbc.Col(
						dbc.Card(
							html.P("TEST")
						)
					),
					dbc.Col(
						dbc.Card(
							html.P("TEST")
						)
					)
				]),
				dbc.Row([
					dbc.Col(
						dbc.Card(
							html.P("TEST")
						)
					),
					dbc.Col(
						dbc.Card(
							html.P("TEST")
						)
					)
				]),
				dbc.Row([
					dbc.Col(
						dbc.Card(
							html.P("TEST")
						)
					),
					dbc.Col(
						dbc.Card(
							html.P("TEST")
						)
					)
				]),
				dbc.Row([
					dbc.Col(
						dbc.Card(
							html.P("TEST")
						)
					),
					dbc.Col(
						dbc.Card(
							html.P("TEST")
						)
					)
				])
			])

body = html.Div([
		dbc.Row([
			dbc.Col(
				html.Div(
					com_cards, style={'overflow': 'auto', 'height': '350px'}
				), style={'width': '100%'}
			),
			dbc.Col(html.Div(id='map'))
		], style={'margin': '5px'}),
		dbc.Row([
			dbc.Col(
				dbc.Card(
					dcc.Graph(id='graph-evolution-pop'), color="light", outline=True, style={'border-radius':'0.5em'})
			, width=4, align="center"),

			dbc.Col(
				dbc.Card(
					dcc.Graph(id='graph-evolution-soc-pro'), color="light", outline=True, style={'border-radius':'0.5em'})
			, width=8)

		], style={'margin-bottom': '5px', 'margin-left': '5px', 'margin-right': '5px'}),
		dbc.Row(
			dbc.Col(
				dbc.Card()
			),
		)
	])


app.layout = html.Div([
	    dcc.Location(id='url', refresh=False),
		navbar,
		dbc.Container([
			dbc.Card(
				body
			, style={'background-color': 'transparent', 'border-color': 'white'})
		], fluid=True)
	], className='mt-0')


@app.callback(dash.dependencies.Output('url', 'pathname'),
              [dash.dependencies.Input('years', 'value')])

def redirect_url(dropdown_value):
    return dropdown_value

@app.callback(
	dash.dependencies.Output('map', 'children'),
	[dash.dependencies.Input('departements', 'value')])

def update_map(selector):
	if len(selector):
		if Path(str(Path.joinpath(STATIC_PATH, 'maps', selector[0])) + '.html').is_file():
			return html.Iframe(srcDoc = open(str(Path.joinpath(STATIC_PATH, 'maps', selector[0])) + '.html', 'r', encoding='utf-8').read(), width='100%', height='400', style={'border-radius':'0.5em'})
		else:
			return html.Iframe(srcDoc = open(str(Path.joinpath(STATIC_PATH, 'maps', 'nodata')) + '.html', 'r', encoding='utf-8').read(), width='100%', height='400', style={'border-radius':'0.5em'})

@app.callback(
	dash.dependencies.Output('communes', 'options'),
	[dash.dependencies.Input('departements', 'value')])

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
			marker = dict(color = 'red'),
			visible = 'legendonly'
			)
		)

		traces.append(dict(
			fill='tozeroy',
			x = x_years,
			y = y_pop_women,
			name = commune+' Femmes',
			marker = dict(size = '10', color = 'blue'),
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
			marker = dict(color = 'green'),
			)
		)

	figure =  {
		'data': traces,
		'layout': dict(
			margin={'t': 40, 'b': 0, 'l': 0, 'r': 0},
			title = "Evolution de la population à {} de {} à {}".format(legend_title, min(years), max(years)),
			xaxis = {'title': 'Année', 'gridcolor' : 'rgba(238, 238, 238, 0)'},
			yaxis = {'title': 'Population', 'gridcolor' : 'rgba(238, 238, 238, 0)'},
			hovermode = 'closest',
			paper_bgcolor =  'rgba(34, 34, 34, 0)',
            plot_bgcolor = 'rgba(34, 34, 34, 0)',
			font = {'color': 'white', 'size': 10},
			legend = dict(orientation="h", y=-0.2),
			height = 300,
		),
	}

	return figure

def update_graph_evolution_soc_pro(selected_commune):
	traces = list()
	all_period = dict()
	n = 0

	for commune in selected_commune:
		categories_soc_pro_commune_years = s.categories_soc_pro_commune(commune)
		x_years = categories_soc_pro_commune_years['years']
		y_pop = dict()
		y_pop_unemployment = list()

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
				name = commune+' '+key,
				marker = dict(color = DEFAULT_PLOTLY_COLORS[n]),
				)
			)

			n += 1

		for key, value in categories_soc_pro_commune_years['unemployment'].items():
			y_pop_unemployment.append(int(value))

		traces.append(dict(
			x = x_years,
			y = y_pop_unemployment,
			name = commune+' Chomeurs',
			marker = dict(color = DEFAULT_PLOTLY_COLORS[n]),
			)
		)
		n += 1

	all_period_years = list(all_period.keys())
	all_period_pop = list(all_period.values())
	legend_title = selected_commune[0]

	if len(selected_commune) > 1:
		legend_title = ", ".join(selected_commune[0:2])+"..."
		traces.append(dict(
			x = all_period_years,
			y = all_period_pop,
			name = legend_title,
			marker = dict(color = 'green'),
			)
		)

	figure =  {
		'data': traces,
		'layout': dict(
			title = "Evolution des catégories socio-profesionnelles à {} de {} à {}".format(legend_title, min(years), max(years)),
			xaxis = {'title': 'Année',  'gridcolor' : 'rgba(238, 238, 238, 0)'},
			yaxis = {'title': 'Population', 'gridcolor' : 'rgba(238, 238, 238, 0)'},
			hovermode = 'closest',
			margin={'t': 40, 'b': 0, 'l': 0, 'r': 0},
			font = {'color': 'white', 'size': 10},
			paper_bgcolor =  'rgba(0, 0, 0, 0)',
            plot_bgcolor = 'rgba(0, 0, 0, 0)',
			legend = dict(orientation="h", y=-0.2,
			)
		),
	}

	return figure

##########Year graphs##########

def update_graph_evolution_pop_year(selected_commune, year):
	population_years = s.get_pop_all_period(selected_commune[0])

	y_pop_men = int(population_years[str(year)][1])
	y_pop_women = int(population_years[str(year)][2])

	traces = [go.Pie(labels=['Hommes', 'Femmes'], values=[y_pop_men, y_pop_women])]

	figure =  {
		'data': traces,
		'layout': dict(
			margin={'t': 40, 'b': 0, 'l': 0, 'r': 0},
			title = "Répartition de la population à {} en {}".format(selected_commune[0], year),
			xaxis = {'title': 'Année', 'gridcolor' : 'rgba(238, 238, 238, 0)'},
			yaxis = {'title': 'Population', 'gridcolor' : 'rgba(238, 238, 238, 0)'},
			hovermode = 'closest',
			paper_bgcolor =  'rgba(34, 34, 34, 0)',
            plot_bgcolor = 'rgba(34, 34, 34, 0)',
			font = {'color': 'white', 'size': 10},
			legend = dict(orientation="h", y=-0.2),
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
				name = key.split('_Actifs_ayant_un_emploi')[0],
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
			title = "Répartition de la population à {} en {}".format(selected_commune[0], year),
			xaxis = {'title': '', 'gridcolor' : 'rgba(238, 238, 238, 0)'},
			yaxis = {'title': 'Population', 'gridcolor' : 'rgba(238, 238, 238, 0)'},
			hovermode = 'closest',
			paper_bgcolor =  'rgba(34, 34, 34, 0)',
            plot_bgcolor = 'rgba(34, 34, 34, 0)',
			font = {'color': 'white', 'size': 10},
			legend = dict(orientation="h", y=-0.2),
			height = 300,
		),
	}

	return figure


@app.callback([
		dash.dependencies.Output('graph-evolution-pop', 'figure'),
		dash.dependencies.Output('graph-evolution-soc-pro', 'figure'),
	],
	[
		dash.dependencies.Input('communes', 'value'),
		dash.dependencies.Input('url', 'pathname'),
	]
	)
def update_card(commune, pathname):
	if pathname == '/' or pathname == None:
		return [update_graph_evolution_pop(commune), update_graph_evolution_soc_pro(commune)]

	elif int(pathname) in years:
		return [update_graph_evolution_pop_year(commune, pathname), update_graph_evolution_soc_pro_year(commune, pathname)]

# print(__name__)
# if __name__ == '__main__':
# 	app.run_server(debug=True)
