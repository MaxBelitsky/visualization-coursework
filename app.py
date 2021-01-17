import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import pandas as pd
import numpy as np
from graph_generation.graph_generation import generate_graph
from graph_generation.interaction import filter_data, select, flip_axes


# Read the data
df = pd.read_excel('data/dataset.xlsx').dropna(how="all", axis=1)
df['select'] = False

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets, title="COVID-19 Visualization Tool")



# This declares the app's layout
app.layout = html.Div(id="main", children=[
    html.Div(id="head", children=[
        html.H1(children='COVID-19 Visualization Tool', id="h1"),
        html.Div(children='''
        This tool is intended to visualize COVID-19 data.
    ''', id="description")]),

    # Dropdown panel container
    html.Div(id='dropdown_panel', children=[
        html.Div(id="dropdown_x_container", children=[
            html.Label("Select X Axis", id="x_axis_label"),
            dcc.Dropdown(id='dropdown_x', value=['Red blood Cells'])]
            ),

        html.Div(id="dropdown_y_container", children=[
            html.Label("Select Y Axis", id="y_axis_label"),
            dcc.Dropdown(id='dropdown_y', value=['Platelets'])]
            )
        ]),
    
    # Main panel container
    html.Div(id='main_panel', children=[dcc.Graph(id='main-graph', config={'displayModeBar': False})]),

    # Side panel container
    html.Div(id='side_panel', children=[
        html.Label("Graph", id="label_graph_type"),
        dcc.RadioItems(
            id='radio_graph_type',
            options=[{'label': 'Histogram', 'value': 'histogram'}, 
                     #{'label': 'Bar plot', 'value': 'bar'}, 
                     {'label': 'Scatter plot', 'value': 'scatter'}],
            value='scatter',
            ),
        html.Label("Options", id="label_options"),
        dcc.Checklist(
            id='checklist_options',
            options=[],
            value=[],
            ),
        html.Label("Color", id="color_label"),
        html.Div(id="color_dropdown_container", children=[
            dcc.Dropdown(id="color_dropdown", value=None, options=[{'label': "Green", 'value': "green"}])
        ]),
        html.Label("Filter", id="label_filter"),
        html.Div(id='dropdown_filter_container', children=[
            dcc.Dropdown(id='dropdown_filter', value=None, options=[{'label': value, 'value': value} for value in df.columns[1:]]),
            ]),
        html.Div(id='slider_filter_container', children=[
            dcc.RangeSlider(
                id='slider_filter',
                step=0.5,
                allowCross=False,
                tooltip={"always_visible": False, "placement": "bottom"},
                updatemode="drag")]),
        # This is invisible label to fill radio items with background
        html.Div(id="flip_button_container", children=[
            html.Button("Flip", id="flip_button", n_clicks=0)
        ]),
        html.Label("Filler", id="filler")
        ])

])



# This callback is used to update the graph based on the chosen attribtes and graph types
@app.callback(
    Output('main-graph', 'figure'),
    Input('dropdown_x', 'value'),
    Input('dropdown_y', 'value'),
    Input('radio_graph_type', 'value'),
    Input('checklist_options', 'value'),
    Input("slider_filter", "value"),
    Input("dropdown_filter", "value"),
    Input('main-graph', 'selectedData'),
    Input('color_dropdown', 'value'),
    Input("flip_button", "n_clicks"))
def update_figure(x, y, graph_type, options, value_filter_slider, value_filter_dropdown, selectedData, color_value, flip_value):
    # Create a dictionary with options and then unpack it in the generate_graph() call
    opts = dict()
    for option in options:
        for key, value in eval(option).items():
            opts[key] = value

    # Flip the axes
    x_y = flip_axes(flip_value, opts, graph_type, x, y)

    # Select points
    select(df, selectedData, graph_type, x, y)

    # Filter the data based on the filter values
    data = filter_data(df, value_filter_dropdown, value_filter_slider)

    # Generate graph
    selected_points = list(data[data['select'] == True].index)
    fig = generate_graph(data, x=x_y[0], y=x_y[1], graph_type=graph_type, selected_points=selected_points, **opts)

    # Make the transition smoother
    fig.update_layout(transition_duration=50, paper_bgcolor='rgba(0,0,0,0)', clickmode='event+select') #dragmode='select'
    
    # Update the color
    if color_value != None:
        fig.update_traces(marker={"color": color_value})

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
    Output('checklist_options', 'options'),
    Input('radio_graph_type', 'value'),
    Input('dropdown_x', 'value'),
    Input('dropdown_y', 'value'))
def dynamic_options(graph_type, value_x, value_y):
    if graph_type == "histogram":
        # Only numerical values for the X are possible
        return ([{'label': value, 'value': value} for value in df.columns[df.dtypes=="float"]], [{'label': "None", 'value': ''}], [])

    elif graph_type == "scatter":
        # Only numerical values for both X and Y axes are possible
        if len(value_x) == 1 and len(value_y) == 1:
            return ([{'label': value, 'value': value} for value in df.columns[df.dtypes=="float"]], 
                    [{'label': value, 'value': value} for value in df.columns[df.dtypes=="float"]],
                    [{'label': 'SARS-Cov-2 test result', 'value': '{"color": "SARS-Cov-2 exam result"}'},
                    #{'label': 'Select Mode', 'value': '{"color": "select"}'},
                    {'label': 'Trendline', 'value': '{"trendline": "ols"}'}
                     ])

        return ([{'label': value, 'value': value} for value in df.columns[df.dtypes=="float"]],
                    [{'label': value, 'value': value} for value in df.columns[df.dtypes=="float"]],
                    [{'label': 'SARS-Cov-2 test result', 'value': '{"color": "SARS-Cov-2 exam result"}'},
                     #{'label': 'Select Mode', 'value': '{"color": "select"}'}
                     ])


@app.callback(Output("slider_filter", "min"),
              Output("slider_filter", "max"),
              Output("slider_filter", "marks"),
              Output("slider_filter", "value"),
              Output("slider_filter", "step"),
              Input("dropdown_filter", "value"))
def adjust_filter_slider(value):
    if value != None:
        if df[value].dtypes == "float64":
            maximum = df.max()[value]
            minimum = df.min()[value]
            middle = minimum + (maximum - minimum)/2
            return (minimum, maximum, {minimum: "{:.1f}".format(minimum), middle: "{:.1f}".format(middle), maximum: "{:.1f}".format(maximum)}, [minimum, maximum], 0.1)

        elif df[value].dtypes == "int64":
            maximum = int(df.max()[value])
            minimum = int(df.min()[value])
            return [minimum, maximum, {minimum: "{}".format(minimum), maximum: "{}".format(maximum)}, [minimum, maximum], 1]

        elif df[value].dtypes == "object":
            length = len(df[value].dropna().unique()) - 1
            marks_dictionary = dict()
            for i in range(length+1):
                marks_dictionary[i] = df[value].dropna().unique()[i]
            return [0, length, marks_dictionary, [0, length], 1]

    return (0, 20, {0: "", 20: ""}, [0, 20], 0.1)


@app.callback(Output("main-graph", "selectedData"),
            Input("flip_button", "n_clicks"),
            Input('checklist_options', 'value'),
            Input("dropdown_filter", "value"),
            Input("slider_filter", "value"))
def clear_data(n_clicks, option, filter, range):
    return None


if __name__ == '__main__':
    app.run_server(debug=True)
