from flask import render_template, url_for, request
import csv
from collections import Counter

from globaldatacommons.models import Country, Categories, Series
from globaldatacommons import app

@app.route("/")
@app.route("/home")
def home():
    return render_template('layout.html', countries =[Country(code='AL1', name='Albania Enhanced', countrystandard='eGDDS')])

@app.route("/about")
def about():
    return "<h1>Allen made this!<h1>"

