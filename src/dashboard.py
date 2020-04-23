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

select_dep = dbc.Col([
				dbc.Label('Départements :', style={'font-size':'15px'}),
				dcc.Dropdown(
					id = 'departements',
					options=[{'label': dep, 'value': dep} for dep in all_options.keys()],
					multi=True,
					value=['74'],
					style={'color':'grey', 'font-size': '15px'},
					placeholder='Départements'
				),
			])

select_com = dbc.Col([
				dbc.Label('Communes :', style={'font-size':'15px'}),
				dcc.Dropdown(
					id = 'communes',
					multi=True,
					value=['Annecy'],
					style={'color':'grey', 'font-size': '15px'},
					placeholder='Communes'   
				),
			])

select_year = dbc.Col([
				dbc.Label('Années :', style={'font-size':'15px'}),
				dcc.Dropdown(
					id = 'years',
					multi=True,
					options=[{'label': year, 'value': year} for year in years],
					style={'color':'grey', 'font-size': '15px'},
					placeholder='Années'   
				),
			])                      

navbar = dbc.Navbar(
	[
		# Use row and col to control vertical alignment of logo / brand
		dbc.Row(
			[
				dbc.Col(html.Img(src='/static/logo_polytech.png', height="45px")),
				dbc.Col(dbc.NavbarBrand("Insee Dashboard", className="ml-2")),
			],
			align="center",
			no_gutters=True,
		),
		select_dep,
		select_com,
		select_year,
	],
	sticky='top',
)

body = dbc.Container([
			dbc.Card([
				dbc.CardBody([
					dbc.Row([
						dbc.Card(
							id='map',
							style={'width': '100%'}
						)
					]),
					dbc.Row([
						dbc.Card([
							dcc.Graph(id='graph-evolution-pop', style={'border-radius':'0.5em'}),
						], style={'border-radius':'0.5em', 'width': '100%'})
					])
				])
			], className='indicateurs_card')
		], fluid=True)
	

app.layout = html.Div([navbar, body])

@app.callback(
	dash.dependencies.Output('map', 'children'),
	[dash.dependencies.Input('departements', 'value')])

def update_map(selector):
	if len(selector):
		return html.Iframe(srcDoc = open(str(Path.joinpath(STATIC_PATH, 'maps', selector[0])) + '.html', 'r', encoding='utf-8').read(), width='100%', height='400', style={'border-radius':'0.5em'})

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

	for commune in selected_commune:
		population_years = s.get_pop_all_period(commune)

		x_years = list()
		y_pop = list()
		for year, pop in population_years.items():
			x_years.append(int(year))
			y_pop.append(int(pop))

		traces.append(dict(
			x = x_years,
			y = y_pop,
			name = commune,
			marker = dict(size = '10', color = 'rgb(55, 83, 109)'),
			)
		)
	figure =  {
		'data': traces,
		'layout': dict(
			title = "Evolution de la population de {} de {} à {}".format(" ".join(selected_commune), min(years), max(years)),
			xaxis = {'title': 'Année'},
			yaxis = {'title': 'Population'},
			hovermode = 'closest',
		),
	}

	return figure


@app.callback([
		dash.dependencies.Output('graph-evolution-pop', 'figure'),
	],
	[
		dash.dependencies.Input('communes', 'value'),
	]
	)
def update_card(commune):
	return [update_graph_evolution_pop(commune),]

if __name__ == '__main__':
	app.run_server(debug=True)
