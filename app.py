import dash
from dash.dependencies import Input, Output
import pandas as pd
import numpy as np
from graph_generation.graph_generation import generate_graph
from graph_generation.interaction import filter_data, select, flip_axes
from graph_generation.exploration import cluster
from layout import generate_layout


# Read the data
df = pd.read_excel('data/dataset.xlsx').dropna(how="all", axis=1)
df = df.iloc[df["Red blood Cells"].dropna().index, :]
df['select'] = False

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets, title="COVID-19 Visualization Tool")


# This declares the app's layout
app.layout = generate_layout(df)


# This callback is used to update the graph based on the chosen attribtes and graph types
@app.callback(
    Output('main-graph', 'figure'),
    Output('second-graph', 'figure'),
    Input('dropdown_x', 'value'),
    Input('dropdown_y', 'value'),
    Input('radio_graph_type', 'value'),
    Input('checklist_options', 'value'),
    Input("slider_filter", "value"),
    Input("dropdown_filter", "value"),
    Input('main-graph', 'selectedData'),
    Input('color_dropdown', 'value'),
    Input("flip_button", "n_clicks"),
    Input("cluster_dropdown", "value"),
    Input("input_cluster", "value"))
def update_figure(x, y, graph_type, options, value_filter_slider, value_filter_dropdown, selectedData, color_value, flip_value, cluster_value, n_clusters):
    fig2 = generate_graph(df, x=[], y=[])
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

    # Cluster
    if cluster_value != None and n_clusters != None and graph_type == "scatter":
        data['Cluster'] = cluster(data, cluster_value, n_clusters)
        data['Cluster'] = data['Cluster'].astype(str)
        opts["color"] = data['Cluster']
        fig2 = generate_graph(data, x=cluster_value, graph_type="box")

    # Generate graph
    selected_points = list(data[data['select'] == True].index)
    fig = generate_graph(data, x=x_y[0], y=x_y[1], graph_type=graph_type, selected_points=selected_points, **opts)

    # Make the transition smoother
    fig.update_layout(transition_duration=50, paper_bgcolor='rgba(0,0,0,0)', clickmode='event+select') #dragmode='select'
    
    # Update the color
    if color_value != None:
        fig.update_traces(marker={"color": color_value})

    return (fig, fig2)


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
    """ Clear the selected data on state change """
    return None


@app.callback(Output("cluster_dropdown", "options"),
            Input('dropdown_x', 'value'),
            Input('dropdown_y', 'value'))
def clustring_options(x_value, y_value):
    """ Generate clustering options """
    values = x_value + y_value
    return ([{'label': value, 'value': value} for value in values])


@app.callback(Output("second-graph", "style"),
            Input('cluster_dropdown', 'value'),
            Input('input_cluster', 'value'))
def show_second_graph(variable, n_clusters):
    if variable != None and n_clusters != None:
        if n_clusters > 1:
            return {"display": "block"}


if __name__ == '__main__':
    app.run_server(debug=True)
