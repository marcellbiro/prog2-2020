import pandas as pd
import numpy as np
import json

input_locations = json.load(open("inputs.json", "r"))

df = pd.read_csv("filtered.csv")

answers = []

for place in input_locations:
    min_distance = np.inf
    closest_place = {}
    for idx, row in df.iterrows():
        distance = (
            (place["lon"] - row["lon"]) ** 2 + (place["lat"] - row["lat"]) ** 2
        ) ** 0.5
        if distance < min_distance:
            min_distance = distance
            closest_place = row[["lon", "lat", "name"]].to_dict()
    answers.append(closest_place.copy())

json.dump(answers, open("outputs.json", "w"))
