import pandas as pd

data_file_path = "data.csv"

df = pd.read_csv(data_file_path)

df.loc[:, ["lon", "lat", "name"]].to_pickle("filtered.pkl")
