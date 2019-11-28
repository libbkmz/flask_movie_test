from flask import Flask, escape, request, render_template
import requests as req

from api import DataProvider

app = Flask(__name__)
data_provider = DataProvider()


@app.route('/')
def hello():
    films, req_times = data_provider.films
    return render_template("main.html", films=films, req_times=req_times)


# if __name__ == "__main__":
#     app.run(host="0.0.0.0", debug=True, use_reloader=False)
