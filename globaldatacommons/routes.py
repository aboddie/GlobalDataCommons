from flask import render_template, url_for, request
from globaldatacommons import app



@app.route("/")
@app.route("/home")
def about():
    render_template('home.html', countries=[])
