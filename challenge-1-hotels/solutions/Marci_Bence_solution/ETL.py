import pandas as pd
import pickle
from sklearn.neighbors import BallTree
import numpy as np
import sys

data_file_path = "data.csv"
df = pd.read_csv(data_file_path)
df = df[['name','lon','lat']]

df.to_pickle('accommodations')


bt = BallTree(df[['lat', 'lon']].values)

with open('Ball_Tree', 'wb') as f:
    pickle.dump(bt, f)
