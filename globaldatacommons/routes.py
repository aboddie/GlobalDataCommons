from flask import render_template, url_for, request
import csv
import os
from collections import Counter

from globaldatacommons.models import Country, Categories, Series
from globaldatacommons import app

@app.route("/")
@app.route("/home")
def home():
    return render_template('layout2Column.html', countries =[Country(code='AL1', name='Albania Enhanced', countrystandard='eGDDS')])

@app.route("/about")
def about():
    return "<h1>Allen made this!<h1>"

@app.route("/report")
def report():
    return f"<h1>My test {os.environ['SQLCONNSTR_GDC_database']}<h1>"
