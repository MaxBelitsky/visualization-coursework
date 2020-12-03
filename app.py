import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import pandas as pd
import numpy as np
from graph_generation import generate_graph


# Read the data
df = pd.read_excel('dataset.xlsx').dropna(how="all", axis=1)

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)



# This declares the app's layout
app.layout = html.Div(children=[
    html.H1(children='COVID-19 Visualization Tool', id="h1", style={'text-align': 'center'}),
    html.Div(children='''
        This is tool that is intended to visualize COVID-19 data.
    ''', style={'text-align': 'center'}),

    # Dropdown panel container
    html.Div(id='dropdown_panel', children=[
        html.Div([
            html.Label("Select X Axis", style={'text-align': 'left',  'margin-bottom': '10px', 'font-size': '16px'}),
            dcc.Dropdown(
                id='dropdown_x',
                #options=[{'label': value, 'value': value} for value in attributes],
                value=['Red blood Cells']
                )], style={'width': '48%', 'display': 'inline-block'}),

        html.Div([
            html.Label("Select Y Axis", style={'text-align': 'left', 'margin-bottom': '10px', 'font-size': '16px'}),
            dcc.Dropdown(
                id='dropdown_y',
                #options=[{'label': value, 'value': value} for value in attributes],
                value=[]
                )], style={'width': '48%', 'float': 'right', 'display': 'inline-block'})
        ], style={'margin-top': '40px'}),
    
    # Main panel container
    html.Div(id='main_panel', children=[
    
        dcc.Graph(
            id='main-graph',
            style={'width': '1200px', 'height': '600px'}
            )
        ], style={'float': 'left', 'margin-top': '0px'}),

    # Side panel container
    html.Div(id='side_panel', children=[
        html.Label("Options", style={'text-align': 'center', 'font-size': '20px', 'margin-bottom': '8px'}),
        dcc.RadioItems(
            id='radio',
            options=[{'label': 'Histogram', 'value': 'histogram'}, 
                     #{'label': 'Bar plot', 'value': 'bar'}, 
                     {'label': 'Scatter plot', 'value': 'scatter'}],
            value='histogram',
            style={'width': '10%', 'float': 'left', 'margin-left': '75px'},
            labelStyle={'display': 'block'},
            ),
        # This is invisible label to fill radio items with background
        html.Label("Filler", style={'text-align': 'center', 'font-size': '20px', 'margin-bottom': '8px', 'visibility': 'hidden'})
        ], style={'margin-top': '48px', 'background': 'rgba(0, 128, 0, 0.04)'})

])



# This callback is used to update the graph based on the chosen attribtes and graph types
@app.callback(
    Output('main-graph', 'figure'),
    Input('dropdown_x', 'value'),
    Input('dropdown_y', 'value'),
    Input('radio', 'value'))
def update_figure(x, y, graph_type):
    fig = generate_graph(df, x=x, y=y, graph_type=graph_type)#, color="SARS-Cov-2 exam result")
    # Make the transition smoother
    fig.update_layout(transition_duration=50)
    return fig


# This callback needs to be updated
# The initial idea was to make the dropdown single if another dropdown is multiple
# But this creates complcations in the input since multiple dropdowns provide lists as outputs and single provide strings
# So for now this callback only returns True, True making both dropdowns multipls
# Maybe we can use this later
@app.callback(
    Output('dropdown_x', 'multi'),
    Output('dropdown_y', 'multi'),
    Input('dropdown_x', 'value'),
    Input('dropdown_y', 'value'))
def on_exit(value_x, value_y):
    """if isinstance(value_x, list) and len(value_x) > 1:
        return (True, True)    
    elif value_y != None and isinstance(value_y, list) and len(value_y) > 1:
        return (True, True)"""
    return (True, True)


# This callback is used to change the options avaliable in the dropdowns (e.g. histogram allows only for x asix entries)
@app.callback(
    Output('dropdown_x', 'options'),
    Output('dropdown_y', 'options'),
    Input('radio', 'value'),
    Input('dropdown_x', 'value'))
def dynamic_options(graph_type, value_x):
    if graph_type == "histogram":
        # Only numerical values for the X are possible
        return ([{'label': value, 'value': value} for value in df.columns[df.dtypes=="float"]], [{'label': "None", 'value': ''}])

    elif graph_type == "scatter":
        # Only numerical values for both X and Y axes are possible
        return ([{'label': value, 'value': value} for value in df.columns[df.dtypes=="float"]], 
                [{'label': value, 'value': value} for value in df.columns[df.dtypes=="float"]])


if __name__ == '__main__':
    app.run_server(debug=True)
