import json
import pandas as pd
import numpy as np
from flask import Flask
from flask import request
from flask import current_app
from sklearn.neighbors import KDTree

app = Flask(__name__)


@app.route("/started")
def started():
    return "FING"


@app.route("/")
def solution():
    input_json = json.load(open("inputs.json", "r"))
    result = current_app.tree.query([[r["lon"], r["lat"]] for r in input_json])
    indexes = [x[0] for x in result[1]]
    out = [{"lon": x[0], "lat": x[1], "name": x[2]} for x in current_app.arr[indexes, :]]
    json.dump(out, open("outputs.json", "w"))
    return "FING"


def shutdown_server():
    func = request.environ.get("werkzeug.server.shutdown")
    if func is None:
        raise RuntimeError("Not running with the Werkzeug Server")
    func()


@app.route("/shutdown")
def shutdown():
    shutdown_server()
    return "Server shutting down..."


app.dfo = (
    pd.read_csv("data.csv")
    .loc[:, ["lon", "lat", "name"]]
    .dropna(how="any")
    .drop_duplicates()
)

app.coords = np.array(app.dfo[["lon", "lat"]])
app.arr = np.array(app.dfo[["lon", "lat", "name"]])
app.tree = KDTree(app.coords, leaf_size=10)


if __name__ == "__main__":
    app.run(debug=True, port=5112)
