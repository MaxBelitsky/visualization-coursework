import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans


def cluster(data, variable, n_clusters):
    X = np.array([data[variable].dropna()]).reshape(-1, 1)
    kmeans = KMeans(n_clusters=n_clusters, random_state=0).fit(X)
    return kmeans.labels_