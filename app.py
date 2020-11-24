import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
import pandas as pd


# Read the data
df = pd.read_excel('dataset.xlsx').dropna(how="all", axis=1)

app = dash.Dash(__name__)

# This is a graph created with Plotly.js
fig = px.scatter(df, x="Red blood Cells", y="Lymphocytes", color="SARS-Cov-2 exam result")

# This declares the app's layout
app.layout = html.Div(children=[
    html.H1(children='COVID-19 Visualization Tool'),

    html.Div(children='''
        This is tool that is intended to visualize COVID-19 data.
    '''),

    html.Br(),
    html.Br(),

    html.Div([
        dcc.Dropdown(
            id='dropdown_x',
            options=[{'label': 'Red Blood Cells', 'value': 'Red blood Cells'}],
            value=['Red blood Cells']
            )], style={'width': '48%', 'display': 'inline-block'}),

    html.Div([
        dcc.Dropdown(
            id='dropdown_y',
            options=[{'label': 'Red Blood Cells', 'value': 'Red blood Cells'}],
            value='Life expectancy at birth, total (years)'
            )], style={'width': '48%', 'float': 'right', 'display': 'inline-block'}),
    
    dcc.Graph(
        id='example-graph',
        figure=fig,
        style={'width': '1400px', 'margin': 'auto'}
    )
])


if __name__ == '__main__':
    app.run_server(debug=True)
