import dash
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import requests
from bs4 import BeautifulSoup
import pandas as pd
import os
#####################################################################################
### get dropdown options
def get_options(list_):
    dict_list = []
    for i in list_:
        dict_list.append({'label': i, 'value': i})
    return dict_list

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
    style={'height': 1000, "background-color": 'rgba(228, 222, 249, 0.65)'},
    children=[
        html.Div([navbar]),
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
            style={},
            children=[ 
            dcc.Graph(id="table")
        ]), 
#################################################################################################
        html.Div(style={'display':'flex'},
            children=[ 
                html.Div(id='age-slider-container', style={'width': '33%','margin-left': 30}),
                html.Div(id='pt-slider-container', style={'width': '33%','margin-left': 30}),
                html.Div(id='ast-slider-container', style={'width': '33%','margin-left': 30}),
            ]),
        html.Div(style={'display':'flex'},
            children=[ 
            html.Div(
                style={'width': '33%'},
                children=[ 
                dcc.RangeSlider(
                    id='age-slider',
                    min=0,
                    max=50,
                    step=1,
                    value=[0,50],
                ),
            ]),
            html.Div(
                style={'width': '33%'},
                children=[ 
                dcc.RangeSlider(
                    id='pt-slider',
                    min=0,
                    max=50,
                    step=1,
                    value=[0,50],
                ),
            ]),
            html.Div(
                style={'width': '33%'},
                children=[ 
                dcc.RangeSlider(
                    id='ast-slider',
                    min=0,
                    max=15,
                    step=1,
                    value=[0,15],
                ),
            ]),
        ]),
##################################################################################################
        html.Div(style={'display':'flex'},
            children=[ 
                html.Div(id='3pt-slider-container', style={'width': '33%','margin-left': 30}),
                html.Div(id='trb-slider-container', style={'width': '33%','margin-left': 30}),
                html.Div(id='ft-slider-container', style={'width': '33%','margin-left': 30}),
            ]),
        html.Div(style={'display':'flex'},
            children=[ 
            html.Div(
                style={'width': '33%'},
                children=[ 
                dcc.RangeSlider(
                    id='3pt-slider',
                    min=0,
                    max=10,
                    step=1,
                    value=[0,10],
                ),
            ]),
            html.Div(
                style={'width': '33%'},
                children=[ 
                dcc.RangeSlider(
                    id='trb-slider',
                    min=0,
                    max=15,
                    step=1,
                    value=[0,15],
                ),
            ]),
            html.Div(
                style={'width': '33%'},
                children=[ 
                dcc.RangeSlider(
                    id='ft-slider',
                    min=0,
                    max=15,
                    step=1,
                    value=[0,15],
                ),
            ]),

        ]),
##################################################################################################
        html.Div(style={'display':'flex'},
            children=[ 
            html.Div(
                style={'width': '33%'},
                children=[ 
                dcc.Dropdown(
                    id='player-picker',
                    placeholder="Select a Player",
                    value=[],
                    multi=True
                )
            ]),
            html.Div(
                style={'width': '33%'},
                children=[ 
                dcc.Dropdown(
                    id='pos-picker',
                    placeholder="Select a Position",
                    value=[],
                    multi=True
                )
            ]),
            html.Div(
                style={'width': '33%'},
                children=[ 
                dcc.Dropdown(
                    id='tm-picker',
                    placeholder="Select a Team",
                    value=[],
                    multi=True
                )
            ]),
        ]),        
    ])

#####################################################################
## Slider labels
@app.callback(
    dash.dependencies.Output('age-slider-container', 'children'),
    [dash.dependencies.Input('age-slider', 'value')])
def update_output(value):
    return f"Age Range: {value}"

@app.callback(
    dash.dependencies.Output('pt-slider-container', 'children'),
    [dash.dependencies.Input('pt-slider', 'value')])
def update_output(value):
    return f"PPG Range: {value}"

@app.callback(
    dash.dependencies.Output('ast-slider-container', 'children'),
    [dash.dependencies.Input('ast-slider', 'value')])
def update_output(value):
    return f"AST Range: {value}"
#####################################################################
@app.callback(
    dash.dependencies.Output('3pt-slider-container', 'children'),
    [dash.dependencies.Input('3pt-slider', 'value')])
def update_output(value):
    return f"3PT Range: {value}"

@app.callback(
    dash.dependencies.Output('trb-slider-container', 'children'),
    [dash.dependencies.Input('trb-slider', 'value')])
def update_output(value):
    return f"TRB Range: {value}"

@app.callback(
    dash.dependencies.Output('ft-slider-container', 'children'),
    [dash.dependencies.Input('ft-slider', 'value')])
def update_output(value):
    return f"FT Range: {value}"
#####################################################################
## Dropdown options
@app.callback(
    dash.dependencies.Output('player-picker', 'options'),
    [dash.dependencies.Input('year-input', 'value')])
def update_dropdown(year):
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

    options=get_options(df['Player'])
    return options

@app.callback(
    dash.dependencies.Output('pos-picker', 'options'),
    [dash.dependencies.Input('year-input', 'value')])
def update_dropdown(year):
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

    options=get_options(df['Pos'].unique())
    return options

@app.callback(
    dash.dependencies.Output('tm-picker', 'options'),
    [dash.dependencies.Input('year-input', 'value')])
def update_dropdown(year):
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

    options=get_options(df['Tm'].unique())
    return options

#####################################################################
## Table update
@app.callback(
    dash.dependencies.Output('table', 'figure'),
    [dash.dependencies.Input('year-input', 'value'),

     dash.dependencies.Input('age-slider', 'value'),
     dash.dependencies.Input('pt-slider', 'value'),
     dash.dependencies.Input('ast-slider', 'value'),

     dash.dependencies.Input('3pt-slider', 'value'),
     dash.dependencies.Input('trb-slider', 'value'),
     dash.dependencies.Input('ft-slider', 'value'),

     dash.dependencies.Input('player-picker', 'value'),
     dash.dependencies.Input('pos-picker', 'value'),
     dash.dependencies.Input('tm-picker', 'value'),])
def update_table(year, age, pt, ast, tpt, trb, ft, player, pos, tm):
    #########################################################################################
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
    #########################################################################################
    df = df[(df['Age'].astype(int) >= age[0]) & (df['Age'].astype(int) <= age[1]) & (df['PTS'].astype(float) >= pt[0]) & (df['PTS'].astype(float) <= pt[1])
            & (df['AST'].astype(float) >= ast[0]) & (df['AST'].astype(float) <= ast[1]) & (df['3P'].astype(float) >= tpt[0]) & (df['3P'].astype(float) <= tpt[1])
            & (df['TRB'].astype(float) >= trb[0]) & (df['TRB'].astype(float) <= trb[1]) & (df['FT'].astype(float) >= ft[0]) & (df['FT'].astype(float) <= ft[1])]
    
    if player != []:
        df = df[(df['Age'].astype(int) >= age[0]) & (df['Age'].astype(int) <= age[1]) & (df['PTS'].astype(float) >= pt[0]) & (df['PTS'].astype(float) <= pt[1])
                    & (df['AST'].astype(float) >= ast[0]) & (df['AST'].astype(float) <= ast[1]) & (df['3P'].astype(float) >= tpt[0]) & (df['3P'].astype(float) <= tpt[1])
                    & (df['TRB'].astype(float) >= trb[0]) & (df['TRB'].astype(float) <= trb[1]) & (df['FT'].astype(float) >= ft[0]) & (df['FT'].astype(float) <= ft[1])
                    & (df['Player'].isin(player))]

    if pos != []:
        df = df[(df['Age'].astype(int) >= age[0]) & (df['Age'].astype(int) <= age[1]) & (df['PTS'].astype(float) >= pt[0]) & (df['PTS'].astype(float) <= pt[1])
                    & (df['AST'].astype(float) >= ast[0]) & (df['AST'].astype(float) <= ast[1]) & (df['3P'].astype(float) >= tpt[0]) & (df['3P'].astype(float) <= tpt[1])
                    & (df['TRB'].astype(float) >= trb[0]) & (df['TRB'].astype(float) <= trb[1]) & (df['FT'].astype(float) >= ft[0]) & (df['FT'].astype(float) <= ft[1])
                    & (df['Pos'].isin(pos))]

    if tm != []:
        df = df[(df['Age'].astype(int) >= age[0]) & (df['Age'].astype(int) <= age[1]) & (df['PTS'].astype(float) >= pt[0]) & (df['PTS'].astype(float) <= pt[1])
                    & (df['AST'].astype(float) >= ast[0]) & (df['AST'].astype(float) <= ast[1]) & (df['3P'].astype(float) >= tpt[0]) & (df['3P'].astype(float) <= tpt[1])
                    & (df['TRB'].astype(float) >= trb[0]) & (df['TRB'].astype(float) <= trb[1]) & (df['FT'].astype(float) >= ft[0]) & (df['FT'].astype(float) <= ft[1])
                    & (df['Tm'].isin(tm))]
            
    #########################################################################################

    fig = go.Figure(
        data= go.Table(
            columnwidth = [100] + [30]*28,
            header=dict(
                values=column_names_clean,
                line = dict(color='rgb(50, 50, 50)'),
                align = ['left'] * 5,
                font = dict(color=['rgb(45, 45, 45)'] * 5, size=14),
                fill = dict(color='rgb(152, 158, 154)'),
            ),
            cells=dict(
                values=[df[k].tolist() for k in df.columns[0:]],
                line = dict(color='#506784'),
                align = ['left'] * 5,
                font = dict(color=['rgb(40, 40, 40)'] * 5, size=12),
                height = 27,
                fill = dict(color=['rgb(211, 211, 211)', 'rgba(211, 211, 211, 0.45)'])
            )
        ),
        layout = go.Layout(
            paper_bgcolor='rgba(0,0,0,0)')
    )

    return fig


if __name__ == '__main__':
    app.run_server(debug=True)
