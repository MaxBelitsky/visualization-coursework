import numpy as np
from sklearn.impute import KNNImputer
import pandas as pd

df = pd.read_excel('../data/dataset.xlsx').dropna(how="all", axis=1)

imputer = KNNImputer(n_neighbors=11)
buff = df.select_dtypes("float64")

df[buff.columns] = imputer.fit_transform(buff)

# Uncomment to save the results as a csv file
#df.to_csv("Imputed.csv")
