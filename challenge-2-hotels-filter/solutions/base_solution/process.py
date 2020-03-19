import pandas as pd
import numpy as np
import json

input_dicts = json.load(open("inputs.json", "r"))

df = pd.read_pickle("filtered.pkl")

min_distances = [np.inf] * len(input_dicts)

answers = [{"missing": True}] * len(input_dicts)

for idx, row in df.iterrows():

    for input_idx, input_dict in enumerate(input_dicts):
        if row["stars"] != input_dict["stars"]:
            continue
        if (row["price"] > input_dict["max_price"]) or (
            row["price"] < input_dict["min_price"]
        ):
            continue
        distance = (
            (input_dict["lon"] - row["lon"]) ** 2
            + (input_dict["lat"] - row["lat"]) ** 2
        ) ** 0.5
        if distance < min_distances[input_idx]:
            min_distances[input_idx] = distance
            answers[input_idx] = row[["lon", "lat", "name", "stars", "price"]].to_dict()

json.dump(answers, open("outputs.json", "w"))
