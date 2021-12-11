import dash
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import dash_table
import requests
from bs4 import BeautifulSoup
import pandas as pd
import fontawesome as fa
import os

#########################################################################################
# scrape data from 2022 table
year = 2022
url = f'https://www.basketball-reference.com/leagues/NBA_{year}_per_game.html'
page = requests.get(url)

soup = BeautifulSoup(page.content, 'html.parser')

table = soup.find_all(class_="full_table")

head = soup.find(class_="thead")
column_names_raw = [head.text for item in head][0]

column_names_clean = column_names_raw.replace("\n", ",").split(",")[2:-1]

players = []
for i in range(len(table)):
    player_ = []
    for td in table[i].find_all("td"):
        player_.append(td.text)
    players.append(player_)
df = pd.DataFrame(players, columns = column_names_clean).set_index("Player")
df.index = df.index.str.replace('*', '')

df = df.reset_index()

df['MP'] = df['MP'].astype(float)
df['FG'] = df['FG'].astype(float)
df['FGA'] = df['FGA'].astype(float)
df['3P'] = df['3P'].astype(float)
df['3PA'] = df['3PA'].astype(float)
df['2P'] = df['2P'].astype(float)
df['2PA'] = df['2PA'].astype(float)
df['FT'] = df['FT'].astype(float)
df['FTA'] = df['FTA'].astype(float)
df['ORB'] = df['ORB'].astype(float)
df['DRB'] = df['DRB'].astype(float)
df['TRB'] = df['TRB'].astype(float)
df['AST'] = df['AST'].astype(float)
df['STL'] = df['STL'].astype(float)
df['BLK'] = df['BLK'].astype(float)
df['TOV'] = df['TOV'].astype(float)
df['PF'] = df['PF'].astype(float)
df['PTS'] = df['PTS'].astype(float)
########################################################################################
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.LUX, 
    {
        'href': 'https://use.fontawesome.com/releases/v5.8.1/css/all.css',
        'rel': 'stylesheet',
        'integrity': 'sha384-50oBUHEmvpQ+1lW4y57PTFmhCaXp0ML5d60M1M7uH2+nqUivzIebhndOJK28anvf',
        'crossorigin': 'anonymous'
    }]
    )
server = app.server

# top nav bar
navbar = dbc.Navbar(
    [
        html.A(
            dbc.Row(
                [
                    dbc.Col(html.I(className="fas fa-basketball-ball"),style={'color': 'white', 'font-size': '30px'}),
                    dbc.Col(dbc.NavbarBrand("NBA Per Game Data", className="ml-2")),
                    
                ],
                align="center",
                no_gutters=True,
            ),
        ),
        dbc.NavbarToggler(id="navbar-toggler", n_clicks=0),
        dbc.Collapse(
            html.A('Original Data', id="link_data", href="", target="_blank", style={'color': 'grey'}),
            id="navbar-collapse",
            is_open=False,
            navbar=True,
        ),
    ],
    color="dark",
    dark=True,
)
##############################################################################################
app.layout = html.Div( 
    style={},
    children=[
        html.Div(
        style={'width': '100%'},
        children=[
            navbar
        ]),
        html.Div(
            style={'margin': 15},
            children=[ 
            dbc.Row(style={'margin-left': 0},
                children=[
                html.H5("Year"),
                html.I(className="fas fa-info-circle", title="Input a year between 1980-present"),
                ]
            ),
            dcc.Input(style={'height': '30px'},
                type="number",
                id='year-input',
                placeholder="Input a Year",
                value=year,
                min=1980, step=1,
            ),
            dbc.Button('Go', id='submit-val', color="secondary", n_clicks=0, style={'padding': 0, 'width': '30px', 'margin': '5px', 'height': '30px'})
        ]),
        html.Div(
            style={'width': '30%', 'margin-left': '5%'},
            children=[
                html.P("Type below each header(s) to filter its data, e.g. >20", 
                    style={'margin': 'auto', 'height': 'auto', 'padding': '10px', 'background-color': 'rgb(17,157,255)', 'color': 'white', 'border-radius': '10px'})
        ]),
        html.Div(
            style={'width': '90%', 'margin-top': '30px', 'margin-bottom': '100px', 'margin-left': 'auto', 'margin-right': 'auto'},
            children=[ 
            dash_table.DataTable(
                    id='datatable-interactivity',
                    columns=[
                        {"name": i, "id": i, "deletable": False, "selectable": False} for i in df.columns
                    ],
                    data=df.to_dict('records'),
                    editable=False,
                    filter_action="native",
                    sort_action="native",
                    sort_mode="multi",
                    column_selectable="single",
                    row_selectable="multi",
                    row_deletable=False,
                    selected_columns=[],
                    selected_rows=[],
                    page_action="native",
                    page_current= 0,
                    page_size= 10,
                    style_table={'overflowX': 'auto'},
                    style_header={
                        'backgroundColor': 'white',
                        'fontWeight': 'bold'
                    },
                    style_cell={
                        'minWidth': '120px', 'maxWidth': '380px',
                        'textAlign': 'left',
                        'padding': '10px'
                    }
                ),
                html.Div(style={'width': 620, 'margin': '100px auto'},
                    children=[
                    html.H5("Graph Metrics"),
                    dcc.Dropdown(style={'width': 200, 'margin-right': 10, 'display': 'inline-grid'},
                        id='column1', options=[{'label': i, 'value': i} for i in df.columns], value="PTS"), 
                    dcc.Dropdown(style={'width': 200, 'margin-right': 10,'display': 'inline-grid'},
                        id='column2', options=[{'label': i, 'value': i} for i in df.columns], value="AST"), 
                    dcc.Dropdown(style={'width': 200, 'display': 'inline-grid'},
                        id='column3', options=[{'label': i, 'value': i} for i in df.columns], value="TRB"),
                    ]),
                html.Div(style={'height': 1000, 'width': '100%', 'margin': '100px auto'}, 
                    id='datatable-interactivity-container')
            ])
    ])

#####################################################################
## Table update
@app.callback(
    Output('datatable-interactivity', 'data'),
    Input('submit-val', 'n_clicks'),
    State('year-input', 'value'))
def update_table(click, year):
    # scrape data from table
    url = f'https://www.basketball-reference.com/leagues/NBA_{year}_per_game.html'
    page = requests.get(url)

    soup = BeautifulSoup(page.content, 'html.parser')

    table = soup.find_all(class_="full_table")

    head = soup.find(class_="thead")
    column_names_raw = [head.text for item in head][0]

    column_names_clean = column_names_raw.replace("\n", ",").split(",")[2:-1]

    players = []
    for i in range(len(table)):
        player_ = []
        for td in table[i].find_all("td"):
            player_.append(td.text)
        players.append(player_)
    df = pd.DataFrame(players, columns = column_names_clean).set_index("Player")
    df.index = df.index.str.replace('*', '')

    df = df.reset_index()

    df['MP'] = df['MP'].astype(float)
    df['FG'] = df['FG'].astype(float)
    df['FGA'] = df['FGA'].astype(float)
    df['3P'] = df['3P'].astype(float)
    df['3PA'] = df['3PA'].astype(float)
    df['2P'] = df['2P'].astype(float)
    df['2PA'] = df['2PA'].astype(float)
    df['FT'] = df['FT'].astype(float)
    df['FTA'] = df['FTA'].astype(float)
    df['ORB'] = df['ORB'].astype(float)
    df['DRB'] = df['DRB'].astype(float)
    df['TRB'] = df['TRB'].astype(float)
    df['AST'] = df['AST'].astype(float)
    df['STL'] = df['STL'].astype(float)
    df['BLK'] = df['BLK'].astype(float)
    df['TOV'] = df['TOV'].astype(float)
    df['PF'] = df['PF'].astype(float)
    df['PTS'] = df['PTS'].astype(float)

    return df.to_dict('records')
#####################################################################
@app.callback(
    Output('datatable-interactivity', 'style_data_conditional'),
    Input('datatable-interactivity', 'selected_columns')
)
def update_styles(selected_columns):
    return [{
        'if': { 'column_id': i },
        'background_color': '#D2F3FF'
    } for i in selected_columns]

@app.callback(
    Output('datatable-interactivity-container', "children"),
    Input('column1', "value"),
    Input('column2', "value"),
    Input('column3', "value"),
    Input('datatable-interactivity', "derived_virtual_data"),
    Input('datatable-interactivity', "derived_virtual_selected_rows"))
def update_graphs(col1, col2, col3, rows, derived_virtual_selected_rows):
    if derived_virtual_selected_rows is None:
        derived_virtual_selected_rows = []

    dff = df if rows is None else pd.DataFrame(rows)

    colors = ['#7FDBFF' if i in derived_virtual_selected_rows else '#0074D9'
              for i in range(len(dff))]

    return [
        dcc.Graph(
            id=column,
            figure={
                "data": [
                    {
                        "x": dff["Player"],
                        "y": dff[column],
                        "type": "bar",
                        "marker": {"color": colors},
                    }
                ],
                "layout": {
                    "xaxis": {"automargin": True},
                    "yaxis": {
                        "automargin": True,
                        "title": {"text": column}
                    },
                    "height": 350,
                    "margin": {"t": 30, "l": 30, "r": 30},
                },
            },
        )
        for column in [col1, col2, col3] if column in dff
    ]

@app.callback(
    Output("navbar-collapse", "is_open"),
    [Input("navbar-toggler", "n_clicks")],
    [State("navbar-collapse", "is_open")],
)
def toggle_navbar_collapse(n, is_open):
    if n:
        return not is_open
    return is_open

@app.callback(
    Output('link_data', 'href'),
    Input('submit-val', 'n_clicks'),
    State('year-input', 'value'))
def update_table(click, year):
    url = f'https://www.basketball-reference.com/leagues/NBA_{year}_per_game.html'
    return url

if __name__ == '__main__':
    app.run_server(debug=True)
