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

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.JOURNAL])
app.title = 'Insee Dashboard'
app.config['suppress_callback_exceptions']=True

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
					options=[{'label': dep, 'value': dep} for dep in all_options.keys()],
					multi=True,
					value=['74'],
					style={'color':'grey', 'font-size': '15px'},
					placeholder='Départements'
				)
			]

select_com = [
				dbc.Label('Communes :', style={'font-size':'15px'}),
				dcc.Dropdown(
					id = 'communes',
					multi=True,
					value=['Annecy'],
					style={'color':'grey', 'font-size': '15px'},
					placeholder='Communes'   
				)
			]

select_year = [
				dbc.Label('Années :', style={'font-size':'15px'}),
				dcc.Dropdown(
					id = 'years',
					multi=True,
					options=[{'label': year, 'value': year} for year in years],
					style={'color':'grey', 'font-size': '15px'},
					placeholder='Années'   
				)]

select_indicator = [
				dbc.Label('Indicateurs :', style={'font-size':'15px'}),
				dcc.Dropdown(
					id = 'indicators',
					multi=True,
					options=[{'label': year, 'value': year} for year in years],
					style={'color':'grey', 'font-size': '15px'},
					placeholder='Indicateurs'   
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
						dbc.Col(select_indicator, className="col-2 ml-4"),
					],
					align='center',
					no_gutters=True,
    				className="flex-nowrap",#ml-auto : margin-left auto, mt-3 : $spacer margin top mt-md-0
    				style={'width': '100%'}
				),
		], sticky='bottom', color="transparent")

body = html.Div([
		dbc.Row([
			dbc.Col(),#Cards
			dbc.Col(html.Div(id='map'))
		]),
		dbc.Row([
			dbc.Col(
				dbc.Card([
					dcc.Graph(id='graph-evolution-pop', style={'border-radius':'0.5em'}),
				], style={'border-radius':'0.5em', 'width': '100%'})
			),
			dbc.Col(
				dbc.Card([
					dcc.Graph(id='graph-evolution-soc-pro', style={'border-radius':'0.5em'}),
				], style={'border-radius':'0.5em', 'width': '100%'})
			)
		])
	])


app.layout = html.Div([
		dbc.Container([
			dbc.Card([
				dbc.CardBody([
					navbar,
					body
				])
			], style={'background-color': '#F8F8FF'})
		], fluid=True)
	], className='mt-1')

@app.callback(
	dash.dependencies.Output('map', 'children'),
	[dash.dependencies.Input('departements', 'value')])

def update_map(selector):
	if len(selector):
		if Path(str(Path.joinpath(STATIC_PATH, 'maps', selector[0])) + '.html').is_file():
			return html.Iframe(srcDoc = open(str(Path.joinpath(STATIC_PATH, 'maps', selector[0])) + '.html', 'r', encoding='utf-8').read(), width='100%', height='450', style={'border-radius':'0.5em'})
		else:
			return html.Iframe(srcDoc = open(str(Path.joinpath(STATIC_PATH, 'maps', 'nodata')) + '.html', 'r', encoding='utf-8').read(), width='100%', height='450', style={'border-radius':'0.5em'})

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
			x = x_years,
			y = y_pop,
			name = commune+' Total',
			marker = dict(size = '10', color = 'rgb(55, 83, 109)'),
			)
		)

		traces.append(dict(
			x = x_years,
			y = y_pop_men,
			name = commune+' Hommes',
			marker = dict(size = '10', color = 'red'),
			visible = 'legendonly'
			)
		)

		traces.append(dict(
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
			x = all_period_years,
			y = all_period_pop,
			name = legend_title,
			marker = dict(size = '10', color = 'green'),
			)
		)

	figure =  {
		'data': traces,
		'layout': dict(
			title = "Evolution de la population à {} de {} à {}".format(legend_title, min(years), max(years)),
			xaxis = {'title': 'Année'},
			yaxis = {'title': 'Population'},
			hovermode = 'closest',
			legend=dict(orientation="h", y=-0.2)
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
				marker = dict(size = '10', color = DEFAULT_PLOTLY_COLORS[n]),
				)
			)

			n += 1

		for key, value in categories_soc_pro_commune_years['unemployment'].items():
			y_pop_unemployment.append(int(value))

		traces.append(dict(
			x = x_years,
			y = y_pop_unemployment,
			name = commune+' Chomeurs',
			marker = dict(size = '10', color = DEFAULT_PLOTLY_COLORS[n]),
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
			marker = dict(size = '10', color = 'green'),
			)
		)

	figure =  {
		'data': traces,
		'layout': dict(
			title = "Evolution des catégories socio-profesionnelles à {} de {} à {}".format(legend_title, min(years), max(years)),
			xaxis = {'title': 'Année'},
			yaxis = {'title': 'Population'},
			hovermode = 'closest',
			legend=dict(orientation="h", y=-0.2)
		),
	}

	return figure


@app.callback([
		dash.dependencies.Output('graph-evolution-pop', 'figure'),
		dash.dependencies.Output('graph-evolution-soc-pro', 'figure'),
	],
	[
		dash.dependencies.Input('communes', 'value'),
	]
	)
def update_card(commune):
	return [update_graph_evolution_pop(commune), update_graph_evolution_soc_pro(commune)]

if __name__ == 'dashboard':
	app.run_server(debug=True)