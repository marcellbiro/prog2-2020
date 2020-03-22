import json
from pykdtree.kdtree import KDTree
import pandas as pd
import numpy as np

input_dicts = tuple(json.load(open("inputs.json", "r")))
df = pd.read_pickle("filtered.pkl")


def filter(data, input_):
    answers = []
    for input_idx, input_dict in enumerate(input_):
        data = data[data['stars'] == input_dict['stars']]
        data = data[data['price'] >= input_dict['min_price']]
        data = data[data['price'] <= input_dict['max_price']]
    
        if len(data) > 0:
            query_all = (input_dict['lat'], input_dict['lon'])
            query_all = np.array(query_all)
            query_all = query_all.reshape(1,-1)
            tree = KDTree(data[['lat', 'lon']].values)
            dist, ind = tree.query(query_all)
            [answers.append(dict(data.iloc[i])) for i in ind]


        else:
            answers.append({"missing": True})
        data = df
    return answers


answers2 = filter(df, input_dicts)

json.dump(answers2,open('outputs.json','w'))
