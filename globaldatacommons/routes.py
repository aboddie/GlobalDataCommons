from flask import render_template, url_for, request
import csv
from collections import Counter

from globaldatacommons.models import Country, Categories, Series
from globaldatacommons import app

@app.route("/")
@app.route("/home")
def about():
    return render_template('home.html', countries =[Country(code='AL1', name='Albania Enhanced', countrystandard='eGDDS')])

