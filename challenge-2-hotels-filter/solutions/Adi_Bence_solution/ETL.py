import pandas as pd

data_file_path = "data.csv"

df = pd.read_csv(data_file_path)

df.drop_duplicates().assign(
    price=lambda _df: _df["current-price"]
    .str[1:]
    .str.replace(",", "")
    .astype(float)
).loc[:, ["lon", "lat", "name", "stars", "price"]].to_pickle("filtered.pkl")
