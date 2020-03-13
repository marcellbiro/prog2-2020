import pandas as pd
import json
from joblib import load

df = pd.read_pickle('filtered.pkl')
tree = load('tree.joblib')
input_df = pd.read_json('inputs.json')

answers = [df.iloc[int(tree.query(input_df[['lon','lat']].values[i].reshape(1, -1), k = 1)[1])].to_dict() for i in range(0,input_df.shape[0])]

json.dump(answers, open("outputs.json", "w"))
