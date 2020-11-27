import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.express as px
import plotly.graph_objs as go
import pandas as pd


# Read the data
df = pd.read_excel('dataset.xlsx').dropna(how="all", axis=1)
#melted = pd.melt(df, id_vars='Patient ID', value_vars=df.columns[:-1])

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)


def generate_graph(data, x="Red blood Cells", y=None, type='histogram', *args, **kwargs):
    """ Generates and returns a graph with the specified arguments """

    if type=="histogram":
        return px.histogram(data, x=x, y=y, **kwargs)

    elif type=="scatter":
        return px.scatter(data, x=x, y=y, **kwargs)

    elif type=="bar":
        return px.bar(data, x=x, y=y, **kwargs)



#attributes = df.iloc[:, 1:].columns
attributes = df.iloc[:, [10, 11, 22]].columns


# This declares the app's layout
app.layout = html.Div(children=[
    html.H1(children='COVID-19 Visualization Tool', style={'text-align': 'center'}),
    html.Div(children='''
        This is tool that is intended to visualize COVID-19 data.
    ''', style={'text-align': 'center'}),

    # Dropdown panel container
    html.Div(id='dropdown_panel', children=[
        html.Div([
            html.Label("Select X Axis", style={'text-align': 'left',  'margin-bottom': '10px', 'font-size': '16px'}),
            dcc.Dropdown(
                id='dropdown_x',
                options=[{'label': value, 'value': value} for value in attributes],
                value='Red blood Cells'
                )], style={'width': '48%', 'display': 'inline-block'}),

        html.Div([
            html.Label("Select Y Axis", style={'text-align': 'left', 'margin-bottom': '10px', 'font-size': '16px'}),
            dcc.Dropdown(
                id='dropdown_y',
                options=[{'label': value, 'value': value} for value in attributes],
                value=None
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
                     {'label': 'Bar plot', 'value': 'bar'}, 
                     {'label': 'Scatter plot', 'value': 'scatter'}],
            value='histogram',
            style={'width': '10%', 'float': 'left', 'margin-left': '75px'},
            labelStyle={'display': 'block'},
            ),
        # This is invisible label to fill radio items with background
        html.Label("Filler", style={'text-align': 'center', 'font-size': '20px', 'margin-bottom': '8px', 'visibility': 'hidden'})
        ], style={'margin-top': '48px', 'background': 'rgba(0, 128, 0, 0.04)'})

])



@app.callback(
    Output('main-graph', 'figure'),
    Input('dropdown_x', 'value'),
    Input('dropdown_y', 'value'),
    Input('radio', 'value'))
def update_figure(x, y, graph_type):
    #if x or y:
    fig = generate_graph(df, x=x, y=y, type=graph_type)#, color="SARS-Cov-2 exam result")
    fig.update_layout(transition_duration=50)
    return fig


@app.callback(
    Output('dropdown_x', 'multi'),
    Output('dropdown_y', 'multi'),
    Input('dropdown_x', 'value'),
    Input('dropdown_y', 'value'))
def on_exit(value_x, value_y):
    if isinstance(value_x, list) and len(value_x) > 1:
        return (True, False)    
    elif value_y != None and isinstance(value_y, list) and len(value_y) > 1:
        return (False, True)

    return (True, True)



if __name__ == '__main__':
    app.run_server(debug=True)
