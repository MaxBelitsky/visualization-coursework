import plotly.express as px
import plotly.graph_objs as go
import pandas as pd
from itertools import zip_longest



def generate_graph(data, x="Red blood Cells", y=None, graph_type='histogram', *args, **kwargs):
    """ Generates and returns a graph with the specified arguments """

    # Return an empty figure if the input is empty
    if x == [] and y==[]:
        return go.Figure()

    # Transform the data into wide format
    melted = pd.melt(data, value_vars=data.columns)

    if graph_type=="histogram":
        return generate_histogram(melted, x, y, "wide")

    elif graph_type=="scatter":
        if len(x) == 1 and len(y) == 1:
            return generate_scatter(data, x[0], y[0], "long", color="SARS-Cov-2 exam result", trendline="ols")

        elif len(x) > 1 or len(y) > 1:
            return generate_scatter_matrix(data, x, y, data_format="long", color="SARS-Cov-2 exam result", **kwargs)

        return generate_scatter(melted, x, y, "wide")





def generate_histogram(data, x, y, data_format="wide", **kwargs):
    """ Generates and returns a histogram """
    if data_format == "wide":
        fig = go.Figure()

        # Iterate over attributes provided in the X Axis dropdown and add traces with histograms
        for attribute in x:
            fig.add_trace(go.Histogram(
                x=data["value"][data["variable"] == attribute],
                y=data["variable"][data["variable"] == attribute],
                name=attribute
                )
            )
        # Make the histograms visible if they overlap
        fig.update_layout(barmode='overlay')
        fig.update_traces(opacity=0.8)
        return fig
    
    elif data_format == "long":
        return px.histogram(data, x, y, **kwargs)




def generate_scatter(data, x, y, data_format="wide", **kwargs):
    """ Generates and returns a scatter plot """
    if data_format == "wide":
        fig = go.Figure()

        # Plot only if 2 variables are chosen, show an empty plot otherwise
        if len(y) > 0 and len(x) > 0:
            
            # This is done to provide a fillvalue for the zip_longest funtion
            if len(x) > len(y):
                previous = y[0]
            else:
                previous = x[0]


            """colors = data["value"][data["variable"] == "SARS-Cov-2 exam result"].to_numpy()
            colors = np.where(colors=="positive", "red", colors)
            colors = np.where(colors=="negative", "blue", colors)"""

            # Loop through the pairs of attributes and add traces to the graph
            # zip_longest makes sure the number of pairs correspond to the lenght of the lognest of two argumens
            # The shorter argument is paired with the previous argument
            for attribute_x, attribute_y in zip_longest(x, y, fillvalue=previous):
                fig.add_trace(go.Scatter(
                    x=data["value"][data["variable"] == attribute_x],
                    y=data["value"][data["variable"] == attribute_y],
                    name=attribute_x + "-" + attribute_y,
                    mode='markers',
                    #trendline="ols"
                    #marker=dict(color=colors)
                    )
                )
            fig.update_layout(legend=dict(
                            orientation="h",
                            yanchor="bottom",
                            y=1.02,
                            xanchor="right",
                            x=1
                            ))
        return fig

    elif data_format == "long":
        return px.scatter(data, x=x, y=y, **kwargs)



def generate_scatter_matrix(data, x, y, data_format="long", **kwargs):
    if data_format == "long":
        dimensions = x + y
        return px.scatter_matrix(data, dimensions=dimensions, **kwargs)