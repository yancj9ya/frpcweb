from flask import Flask
import os


def create_app():
    app = Flask(__name__, static_folder="static")
    app.config["SECRET_KEY"] = os.urandom(24)
    app.config["TEMPLATES_AUTO_RELOAD"] = True
    app.config["JSON_AS_ASCII"] = False

    with app.app_context():
        from . import routes

    @app.after_request
    def after_request(response):
        if response.mimetype == "text/html":
            response.headers["Content-Type"] = "text/html; charset=utf-8"
        return response

    return app
