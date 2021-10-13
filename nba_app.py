import dash
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import dash_table
import requests
from bs4 import BeautifulSoup
import pandas as pd
import os

#########################################################################################
# scrape data from 2021 table
url = f'https://www.basketball-reference.com/leagues/NBA_2021_per_game.html'
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
for i in ['PTS']: 
      df[i]  =  df[i].astype('float64')
########################################################################################
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.LUX])
server = app.server

PLOTLY_LOGO = "https://images.plot.ly/logo/new-branding/plotly-logomark.png"

navbar = dbc.Navbar(
    [
        html.A(
            dbc.Row(
                [
                    dbc.Col(html.Img(src=PLOTLY_LOGO, height="30px")),
                    dbc.Col(dbc.NavbarBrand("NBA Per Game Data", className="ml-2")),
                ],
                align="center",
                no_gutters=True,
            ),
        ),
    ],
    color="dark",
    dark=True,
)
##############################################################################################
app.layout = html.Div( 
    style={'height': 2000},
    children=[
        html.Div(
        style={'width': '100%'},
        children=[
            navbar
        ]),
        html.Div(
            style={'margin': 15},
            children=[ 
            html.H5("Year"),
            dcc.Input(
                id='year-input',
                placeholder="Input a Year",
                value=2021,
            )
        ]),
        html.Div(
            style={'height': 500, 'width': '100%', 'margin': '100px auto'},
            children=[ 
            dash_table.DataTable(
                    id='datatable-interactivity',
                    columns=[
                        {"name": i, "id": i, "deletable": False, "selectable": False} for i in df.columns
                    ],
                    data=df.to_dict('records'),
                    editable=True,
                    filter_action="native",
                    sort_action="native",
                    sort_mode="multi",
                    column_selectable="single",
                    row_selectable="multi",
                    row_deletable=True,
                    selected_columns=[],
                    selected_rows=[],
                    page_action="native",
                    page_current= 0,
                    page_size= 10,
                    style_table={'overflowX': 'auto'},
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
    [Input('year-input', 'value'),])
def update_table(year):
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

if __name__ == '__main__':
    app.run_server(debug=True)
