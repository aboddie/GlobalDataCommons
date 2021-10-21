from collections import namedtuple

from flask import render_template, url_for, request

from .models import Country, Categories, Series
from . import app

@app.context_processor
def utility_processor():
    def dsd_version(signaturestring):
        Structure_Signature = namedtuple("Structure_Signature","stype,agencyID,ID,version")
        version = min(eval(signaturestring)).version # TODO clean up
        if version is not None:
            return version
        else:
            return 'version not specified'    
    return dict(dsd_version=dsd_version) 

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
    category_info = Categories.query.filter(Categories.countrycode==countrycode, Categories.categorycode==domain).first()
    return render_template('CountryDomains.html', country_info=country_info, country=countrydata, category_info=category_info)

@app.route("/report")
def report():
    return render_template('report.html', countries=Country.query.order_by(Country.name).all())

@app.route('/reportview/<countrycode>')
def country_report(countrycode):
    #TODO clean this up
    country = Country.query.filter(Country.code==countrycode).first()
    datadomains = Categories.query.filter(Categories.countrycode==countrycode).all()
    domainreport = []
    total = [0,0,0,0]
    for domain in datadomains:
        if domain.has_error:
            domainreport.append((domain.description, domain.error_text))
        else:
            num = domain.series_count
            numtrue = domain.readable_series
            numfalse = num - numtrue
            precent = f'{numtrue/num:.1%}'
            domainreport.append((domain.description, numtrue, numfalse, num, precent, domain.categorycode, domain.countrycode))
            total[0] += numtrue
    try: 
        total[2] = country.series_count
        total[1] = country.series_count - total[0]
        total[3] = f'{total[0]/country.series_count:.1%}'
    except ZeroDivisionError:
        total[3] = "N.A."
    return render_template('CountryReport.html', country=domainreport, total=total)

@app.route("/about")
def about():
    return render_template('layout.html')#"<h1>Allen made this!<h1>"
