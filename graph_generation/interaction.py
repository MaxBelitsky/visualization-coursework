import numpy as np


def filter_data(df, value_filter_dropdown, value_filter_slider):
    """ Filters a dataframe by a value and retunrs it """
    if value_filter_dropdown != None and df[value_filter_dropdown].dtypes == "float64":
        data = df[(df[value_filter_dropdown] >= value_filter_slider[0]) & (df[value_filter_dropdown] <= value_filter_slider[1])]

    elif value_filter_dropdown != None and (df[value_filter_dropdown].dtypes == "object" or df[value_filter_dropdown].dtypes == "int64"):
        if df[value_filter_dropdown].dtypes == "int64":
            indices = list(range(value_filter_slider[0], value_filter_slider[-1]+1))
        else:
            indices = df[value_filter_dropdown].dropna().unique()[list(set(value_filter_slider))]
        data = df[df[value_filter_dropdown].isin(indices)]

    else:
        data = df
    
    # Reset the indexes to match the point numbers on the graph
    data.reset_index(drop=True, inplace=True)

    return data


def select(df, selectedData, graph_type, x, y):
    """ Modifies a list of selected points """
    if selectedData and graph_type == "scatter":
        for p in selectedData['points']:
            if df.loc[p['pointIndex'], 'select'] == False:
                df.loc[(df[x[0]] == p['x']) & (df[y[0]] == p['y']), 'select'] = True
            else:
                df.loc[(df[x[0]] == p['x']) & (df[y[0]] == p['y']), 'select'] = False


def flip_axes(flip_value, opts, graph_type, x, y):
    if flip_value % 2 != 0:
        if graph_type == "histogram":
            opts['orientation'] = 'h'
        else:
            return [y, x]
    return [x, y]