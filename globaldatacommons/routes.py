from flask import render_template, url_for, request
from globaldatacommons import app



@app.route("/")
@app.route("/home")
def about():
    return "<h1>Allen made this!<h1>"
