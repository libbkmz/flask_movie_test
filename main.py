import requests
from flask import Flask, render_template, Blueprint

from api import DataProvider

data_provider = DataProvider()
main_blueprint = Blueprint("movies", __name__)


def create_app():
    app = Flask(__name__)
    app.register_blueprint(main_blueprint)

    return app


@main_blueprint.errorhandler(requests.exceptions.RequestException)
def request_exception_handler(e):
    return "No data from External API", 500


@main_blueprint.route('/movies')
def hello():
    films, req_times = data_provider.films
    return render_template("main.html", films=films, req_times=req_times)
