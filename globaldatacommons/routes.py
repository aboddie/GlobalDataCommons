from flask import render_template, url_for, request
import csv
from collections import Counter

from globaldatacommons.models import Country, Categories, Series
from globaldatacommons import app


def pullindicators(countryname):
    indicatorlist = []
    inputfilelocation = 'globaldatacommons/static/data.csv' 
    with open(inputfilelocation, 'r', encoding='utf-8-sig') as csvfileread:
        filereader = csv.DictReader(csvfileread, delimiter=',') 
        for row in filereader:
            if countryname == row['Country']:
                indicatorlist.append({'description': row['Description'], 'inSDMX': row['inSDMX'], 'indent': row['Level'], 'data': row['Data'], 'sdmx_data': row['SDMX_Data'], 'dates': row['Dates'], 'source': row['Source']})           
    return indicatorlist

def pullcountryname(countrycode):
    name = Country.query.filter(Country.code==countrycode).first().name 
    return name

@app.route("/")
@app.route("/home")
def home():
    return render_template('home.html', countries=Country.query.all())

@app.route("/about")
def about():
    return "<h1>Allen made this!<h1>"

@app.route('/countryview/<country>')
def country_pages(country):
    if country == 'AL1':
        countryindicators = pullindicators('Albania')
        mydomain = "Consumer Price Index"
        return render_template('ALB_JAM.html', chart='TRUE', title=country, domain=mydomain, country=countryindicators)
    elif country == 'JA1':
        countryindicators = pullindicators('Jamaica')
        mydomain = "Consumer Price Index"
        return render_template('ALB_JAM.html', chart='TRUE', title=country, domain=mydomain, country=countryindicators)
    else:
        datadomains = Categories.query.filter(Categories.countrycode==country).all()
        country_name = pullcountryname(country)
        return render_template('CountryPages.html', title=country_name, listitems=datadomains)

@app.route('/dataview/<country>/<domain>')
def country_domain(country,domain):
    countrydata = Series.query.filter(Series.countrycode==country,Series.categorycode==domain)
    country_name = pullcountryname(country)
    return render_template('CountryDomains.html', title=country_name, country=countrydata)

@app.route("/report")
def report():
    return render_template('report.html', countries=Country.query.all())

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
            All_series = Series.query.with_entities(Series.inECOFIN).filter(Series.countrycode==country,Series.categorycode==domain.categorycode).all()
            All_series = [x[0] for x in All_series]
            Anewlist = dict(Counter(All_series).most_common()) 
            numtrue = Anewlist.get(True,0)
            numfalse = Anewlist.get(False,0)
            num = numtrue + numfalse 
            precent = f'{numtrue/num:.1%}'
            countrydata.append((domain.description, numtrue, numfalse, num, precent, domain.categorycode, domain.countrycode))
            total[0] += numtrue
            total[1] += numfalse
            total[2] += num 
    try: 
        total[3] = f'{total[0]/total[2]:.1%}'
    except ZeroDivisionError:
        total[3] = "N.A."
    country_name = pullcountryname(country)
    return render_template('CountryReport.html', title=country_name, country=countrydata, total=total)
