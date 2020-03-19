import numpy as np
from sklearn.neighbors import KDTree
import pandas as pd
import json

input_locations = json.load(open('inputs.json', 'r'))
df = pd.read_pickle('filtered.pkl')
answers, query_all = [], []
[query_all.append(tuple(dic.values())) for dic in input_locations]
tree = KDTree(np.deg2rad(df[['lat', 'lon']].values), metric = 'euclidean', leaf_size = 400)
dist, ind = tree.query(np.deg2rad(query_all))
[answers.append(dict(df.iloc[i[0]])) for i in ind]
json.dump(answers,open('outputs.json','w'))
