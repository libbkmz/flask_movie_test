from flask import Flask, render_template
from api import DataProvider

app = Flask(__name__)
data_provider = DataProvider()


@app.route('/movies')
def hello():
    films, req_times = data_provider.films
    return render_template("main.html", films=films, req_times=req_times)
