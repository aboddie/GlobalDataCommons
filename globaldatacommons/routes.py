from flask import render_template, url_for, request
import csv
from collections import Counter

from globaldatacommons.models import Country, Categories, Series
from globaldatacommons import app

@app.route("/")
@app.route("/home")
def home():
    return render_template('home.html', countries=Country.query.all())

@app.route("/about")
def about():
    return "<h1>Allen made this!<h1>"

@app.route('/countryview/<country>')
def country_pages(country):
    return "<h1>Allen made this!<h1>"

@app.route("/report")
def report():
    return "<h1>Allen made this!<h1>"
