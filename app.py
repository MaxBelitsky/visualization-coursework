import dash
from dash.dependencies import Input, Output, State
import pandas as pd
import numpy as np
from graph_generation.graph_generation import generate_graph
from graph_generation.interaction import filter_data, select, flip_axes
from graph_generation.exploration import cluster
from layout import generate_layout


# Read the data
df = pd.read_excel('data/dataset.xlsx', engine='openpyxl').dropna(how="all", axis=1)
df = df.iloc[df["Red blood Cells"].dropna().index, :]
df['select'] = False
df["COVID-19"] = pd.get_dummies(df['SARS-Cov-2 exam result'], drop_first=True)


external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets, title="ClinVis")


# This declares the app's layout
app.layout = generate_layout(df, app)


# This callback is used to update the graph based on the chosen attribtes and graph types
@app.callback(
    Output('main-graph', 'figure'),
    Output('second-graph', 'figure'),
    Input('dropdown_x', 'value'),
    Input('dropdown_y', 'value'),
    Input('dropdown_z', 'value'),
    Input('radio_graph_type', 'value'),
    Input('checklist_options', 'value'),
    Input("slider_filter", "value"),
    Input("dropdown_filter", "value"),
    Input('main-graph', 'selectedData'),
    Input("flip_button", "n_clicks"),
    Input("cluster_dropdown", "value"),
    Input("input_cluster", "value"))
def update_figure(x, y, z, graph_type, options, value_filter_slider, value_filter_dropdown, selectedData, flip_value, cluster_value, n_clusters):
    fig2 = generate_graph(df, x=[], y=[])
    explore = False     # Indicates if "Explore" option is chosen
    # Create a dictionary with options and then unpack it in the generate_graph() call
    opts = dict()
    for option in options:
        for key, value in eval(option).items():
            if key != 'explore':
                opts[key] = value
            else:
                explore = True

    # Flip the axes if the "Flip" button is pressed
    x_y = flip_axes(flip_value, opts, graph_type, x, y)

    # Select points
    select(df, selectedData, graph_type, x, y)

    # Filter the data based on the filter values
    data = filter_data(df, value_filter_dropdown, value_filter_slider)

    # Cluster
    if cluster_value != None and n_clusters != None and graph_type == "scatter" and explore == True:
        data['Cluster'] = cluster(data, cluster_value, n_clusters)
        data['Cluster'] = data['Cluster'].astype(str)
        opts["color"] = data['Cluster']
        fig2 = generate_graph(data, x=cluster_value, graph_type="box")

    # Generate graph
    selected_points = list(data[data['select'] == True].index)
    fig = generate_graph(data, x=x_y[0], y=x_y[1], z=z, graph_type=graph_type, selected_points=selected_points, **opts)

    # Make the transition smoother
    fig.update_layout(transition_duration=50, paper_bgcolor='rgba(0,0,0,0)', clickmode='event+select')

    return (fig, fig2)


# This callback is used to change the options avaliable in the dropdowns
@app.callback(
    Output('dropdown_x', 'options'),
    Output('dropdown_y', 'options'),
    Output('dropdown_z', 'options'),
    Output('checklist_options', 'options'),
    Input('radio_graph_type', 'value'),
    Input('dropdown_x', 'value'),
    Input('dropdown_y', 'value'))
def dynamic_options(graph_type, value_x, value_y):
    """ Generate options for the input dropdowns based on the graph type """

    if graph_type == "histogram":
        # Only numerical values for the X are possible
        return ([{'label': value, 'value': value} for value in df.columns[df.dtypes=="float"]], [], [], [])

    elif graph_type == "scatter":
        # Only numerical values for both X and Y axes are possible
        if len(value_x) == 1 and len(value_y) == 1:
            return ([{'label': value, 'value': value} for value in df.columns[df.dtypes=="float"]], 
                    [{'label': value, 'value': value} for value in df.columns[df.dtypes=="float"]],
                    [],
                    [{'label': 'SARS-Cov-2 test result', 'value': '{"color": "SARS-Cov-2 exam result"}'},
                    {'label': 'Explore Mode', 'value': '{"explore": True}'},
                    {'label': 'Trendline', 'value': '{"trendline": "ols"}'}
                     ])

        return ([{'label': value, 'value': value} for value in df.columns[df.dtypes=="float"]],
                    [{'label': value, 'value': value} for value in df.columns[df.dtypes=="float"]],
                    [],
                    [{'label': 'SARS-Cov-2 test result', 'value': '{"color": "SARS-Cov-2 exam result"}'}])

    elif graph_type == "heatmap":
        return ([{'label': value, 'value': value} for value in df.columns[df.dtypes=="float"]],
        [{'label': value, 'value': value} for value in df.columns[df.dtypes=="float"]],
        [],
        [])

    elif graph_type == "par_coords":
        return ([{'label': value, 'value': value} for value in df.columns[df.dtypes=="float"]],
        [{'label': value, 'value': value} for value in df.columns[df.dtypes=="float"]],
        [],
        [{'label': 'SARS-Cov-2 test result', 'value': '{"color": "COVID19"}'}])

    elif graph_type == "strip":
        return ([{'label': value, 'value': value} for value in df.columns[df.dtypes=="int64"].to_list()+df.columns[df.dtypes=="object"][1:].to_list()],
        [{'label': value, 'value': value} for value in df.columns[df.dtypes=="float"]],
        [],
        [{'label': 'SARS-Cov-2 test result', 'value': '{"color": "SARS-Cov-2 exam result"}'}])

    elif graph_type == "ternary":
        return ([{'label': value, 'value': value} for value in df.columns[df.dtypes=="float"]],
        [{'label': value, 'value': value} for value in df.columns[df.dtypes=="float"]],
        [{'label': value, 'value': value} for value in df.columns[df.dtypes=="float"]], 
        [{'label': 'SARS-Cov-2 test result', 'value': '{"color": "SARS-Cov-2 exam result"}'}])


@app.callback(Output("slider_filter", "min"),
              Output("slider_filter", "max"),
              Output("slider_filter", "marks"),
              Output("slider_filter", "value"),
              Output("slider_filter", "step"),
              Input("dropdown_filter", "value"))
def adjust_filter_slider(value):
    """ Adjust the ranges of the filtering slider based on the variable type """

    if value != None:
        if df[value].dtypes == "float64":
            maximum = df.max()[value]
            minimum = df.min()[value]
            middle = minimum + (maximum - minimum)/2
            return (minimum,
                    maximum,
                    {minimum: "{:.1f}".format(minimum), middle: "{:.1f}".format(middle), maximum: "{:.1f}".format(maximum)},
                    [minimum, maximum],
                    0.1)

        elif df[value].dtypes == "int64":
            maximum = int(df.max()[value])
            minimum = int(df.min()[value])
            return (minimum,
                    maximum,
                    {minimum: "{}".format(minimum), maximum: "{}".format(maximum)},
                    [minimum, maximum],
                    1)

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
            Input('input_cluster', 'value'),
            Input('checklist_options', 'value'))
def show_second_graph(variable, n_clusters, options):
    """ Shows second graph """

    if any("explore" in option for option in options):
        if variable != None and n_clusters != None and n_clusters > 1:
            return {"display": "block"}


@app.callback(Output("cluster_dropdown", "style"),
            Output("input_cluster_container", "style"),
            Output("cluster_label", "style"),
            Input('checklist_options', 'value'),
            Input('radio_graph_type', 'value'))
def show_clustering_controls(options, graph_type):
    """ Shows a dropdown and a input field for clustering """

    if any("explore" in option for option in options) and graph_type == "scatter":
        return ({"display": "block"}, {"display": "block"}, {"display": "block"})
    return ({"display": "none"}, {"display": "none"}, {"display": "none"})


@app.callback(Output("dropdown_x_container", "style"),
                Output("dropdown_y_container", "style"),
                Output("dropdown_z_container", "style"),
                Output("x_axis_label", "children"),
                Output("y_axis_label", "children"),
                Output("z_axis_label", "children"),
                Output("flip_button_container", "style"),
                Input('radio_graph_type', 'value'))
def adjust_dropdowns(graph_type):
    """ Dynamically adjust the input dropdowns based on the graph type """

    if graph_type == "histogram":
        return ({"width": "46%", "display": "inline-block"},
                {"display": "none"}, {"display": "none"},
                "Choose variable(s)",
                "",
                "",
                None)

    elif graph_type == "par_coords":
        return ({"width": "46%", "display": "inline-block"},
                {"display": "none"}, {"display": "none"},
                "Choose variable(s)",
                "",
                "",
                {"display": "none"})

    elif graph_type in ["scatter", "heatmap", "strip"]:
        return ({"width": "46%", "display": "inline-block"},
                {"width": "46%", "display": "inline-block"},
                {"display": "none"},
                "Select X Axis",
                "Select Y Axis",
                "",
                None)

    elif graph_type == "ternary":
        return ({"width": "30%", "display": "inline-block", 'float': 'none', 'margin-right': '5%'},
                {"width": "30%", "display": "inline-block", 'float': 'none', 'margin-right': '5%'},
                {"width": "30%", "display": "inline-block", 'float': 'none'},
                "Select X Axis",
                "Select Y Axis",
                "Select Z Axis",
                {"display": "none"})

    return (None, None, None, "", "", "", None)


@app.callback(Output('checklist_options', 'value'),
                Output("flip_button", "n_clicks"),
                Input('radio_graph_type', 'value'))
def clear_options(graph_type):
    """ Clear the options and reset the flip button on state change """
    return ([], 0)


if __name__ == '__main__':
    app.run_server(debug=True)
