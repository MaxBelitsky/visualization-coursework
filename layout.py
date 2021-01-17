import dash_core_components as dcc
import dash_html_components as html


def generate_layout(df):
    layout = html.Div(id="main", children=[
                html.Div(id="head", children=[
                    html.H1(children='COVID-19 Visualization Tool', id="h1"),
                    html.Div(children='''
                    This tool is intended to visualize COVID-19 data.
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
    return layout