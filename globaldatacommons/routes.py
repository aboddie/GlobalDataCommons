from flask import render_template, url_for, request
import csv

from .models import Country, Categories, Series
from . import app


@app.route("/")
@app.route("/home")
def home():
    return render_template('home.html', countries=Country.query.order_by(Country.name).all())

@app.route('/countryview/<countrycode>')
def country_pages(countrycode):
    return render_template('CountryPages.html', 
                            listitems=Categories.query.filter(Categories.countrycode==countrycode).all(), 
                            country_info=Country.query.filter(Country.code==countrycode).first())

@app.route('/dataview/<countrycode>/<domain>')
def country_domain(countrycode,domain):
    countrydata = Series.query.filter(Series.countrycode==countrycode,Series.categorycode==domain)
    country_info = Country.query.filter(Country.code==countrycode).first()
    return render_template('CountryDomains.html', country_info=country_info, country=countrydata)

@app.route("/report")
def report():
    return render_template('report.html', countries=Country.query.order_by(Country.name).all())

@app.route('/reportview/<country>')
def country_report(country):
    #TODO clean this up
    datadomains = Categories.query.filter(Categories.countrycode==country).all()
    countrydata = []
    total = [0,0,0,0]
    for domain in datadomains:
        if domain.has_error:
            countrydata.append((domain.description, domain.error_text))
        else:
            num = domain.series_count
            numtrue = domain.readable_series
            numfalse = num - numtrue
            precent = f'{numtrue/num:.1%}'
            countrydata.append((domain.description, numtrue, numfalse, num, precent, domain.categorycode, domain.countrycode))
            total[0] += numtrue
            total[1] += numfalse
            total[2] += num 
    try: 
        total[3] = f'{total[0]/total[2]:.1%}'
    except ZeroDivisionError:
        total[3] = "N.A."
    return render_template('CountryReport.html', country=countrydata, total=total)

@app.route("/about")
def about():
    return "<h1>Allen made this!<h1>"
