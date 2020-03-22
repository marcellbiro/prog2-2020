import pandas as pd
import json
from joblib import load
import numpy as np
sample_df = pd.read_pickle('filtered.pkl')

input_df = pd.read_json('inputs.json')
df_order = []
answers = [{"missing": True}] * len(input_df)

for i in range(input_df.shape[0]):
  
    star=input_df.loc[i][2]
    if star in sample_df['stars']:
        df=sample_df.loc[star, 'data']
        tree=sample_df.loc[star, 'tree']
        df_order = [df.iloc[hotel] \
                     for hotel in tree.query(input_df[['lon','lat']].\
                                             values[i].reshape(1, -1), k = len(df))[1]]
        df_order[0]['order'] = np.arange(len(df_order[0]))
        answer = df_order[0].loc[(df_order[0].price > input_df['min_price'].values[i]) \
                       & (df_order[0].price < input_df['max_price'].values[i])]
        
        answer = answer[answer['order']==answer['order'].min()]
        if not answer.empty:
            answer['missing'] = False
            answers[i] = answer[['missing',"lon", "lat", "name", "stars", "price"]].to_dict('records')[0]
    else:
        continue

json.dump(answers, open("outputs.json", "w"))

