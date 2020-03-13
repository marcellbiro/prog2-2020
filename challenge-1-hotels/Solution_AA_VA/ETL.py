import pandas as pd
from joblib import dump
from sklearn.neighbors import KDTree

data_file_path = "data.csv"

df = pd.read_csv(data_file_path).drop_duplicates().reset_index(drop = True)
df.loc[:, ['lon','lat','name']].to_pickle('filtered.pkl')

dump(KDTree(df[['lon','lat']].values, leaf_size = 40), 'tree.joblib')
