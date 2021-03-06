import dash_core_components as dcc
import dash_html_components as html


def generate_layout(df, app):
    layout = html.Div(id="main", children=[
                html.Div(id="head", children=[
                    html.Div(id="logo", children=[
                        html.Img(src=app.get_asset_url('logo.jpeg'), style={'height':'5%', 'width':'10%'})
                    ]),
                    html.Div(children='''
                    A tool intended to visualize clinical data.
                ''', id="description")]),

                # Dropdown panel container
                html.Div(id='dropdown_panel', children=[
                    html.Div(id="dropdown_x_container", children=[
                        html.Label("Select X Axis", id="x_axis_label"),
                        dcc.Dropdown(id='dropdown_x', value=['Red blood Cells'], multi=True)]
                        ),

                    html.Div(id="dropdown_y_container", children=[
                        html.Label("Select Y Axis", id="y_axis_label"),
                        dcc.Dropdown(id='dropdown_y', value=['Platelets'], multi=True)]
                        ),

                    html.Div(id="dropdown_z_container", children=[
                        html.Label("Select Z Axis", id="z_axis_label"),
                        dcc.Dropdown(id='dropdown_z', value=['Leukocytes'], multi=True)]
                        )
                    ]),
                
                # Main panel container
                html.Div(id='main_panel', children=[
                    dcc.Graph(id='main-graph', config={'displayModeBar': False}),
                    dcc.Graph(id='second-graph', config={'displayModeBar': False}),
                    ]),

                # Side panel container
                html.Div(id='side_panel', children=[
                    html.Label("Graph", id="label_graph_type"),
                    dcc.RadioItems(
                        id='radio_graph_type',
                        options=[{'label': 'Histogram', 'value': 'histogram'}, 
                                {'label': 'Scatter plot', 'value': 'scatter'},
                                {'label': 'Heatmap', 'value': 'heatmap'},
                                {'label': 'Parallel Coords', 'value': 'par_coords'},
                                {'label': 'Strip', 'value': 'strip'},
                                {'label': 'Ternary', 'value': 'ternary'}],
                        value='scatter',
                        ),
                    html.Label("Options", id="label_options"),
                    dcc.Checklist(
                        id='checklist_options',
                        options=[],
                        value=[],
                        ),
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
                    html.Div(id="flip_button_container", children=[
                        html.Button("Flip", id="flip_button", n_clicks=0)
                    ]),
                    html.Label("Clustering", id="cluster_label"),
                    html.Div(id="cluster_dropdown_container", children=[
                        dcc.Dropdown(id="cluster_dropdown", value=None)
                    ]),
                    html.Div(id='input_cluster_container', children=[
                        dcc.Input(id="input_cluster", type="number", placeholder="n", min=1)
                    ]),
                    # This is invisible label to fill radio items with background
                    html.Label("Filler", id="filler")
                    ])

            ])
    return layout