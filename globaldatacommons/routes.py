from collections import namedtuple

from flask import render_template, url_for, request, _app_ctx_stack
from sqlalchemy.orm import scoped_session

from .models import Country, Categories, Series
from . import app
from . import Session
from . import ReviewSession
from . import BaselineSession

session = scoped_session(Session, scopefunc=_app_ctx_stack.__ident_func__)
reviewSession = scoped_session(ReviewSession, scopefunc=_app_ctx_stack.__ident_func__)
baselineSession = scoped_session(BaselineSession, scopefunc=_app_ctx_stack.__ident_func__)

@app.context_processor
def utility_processor():
    def dsd_version(signaturestring):
        Structure_Signature = namedtuple("Structure_Signature","stype,agencyID,ID,version")
        try:
            sig = eval(signaturestring) # TODO clean up
            if type(sig) == set:
                sig = min(sig)
            version = sig.version
        except:
            version = None

        if version is not None:
            return version
        else:
            return 'version not specified'    
    return dict(dsd_version=dsd_version) 

@app.route("/")
@app.route("/home")
def home():
    return render_template('home.html', 
                            countries=session.query(Country).order_by(Country.name).all(), 
                            link_to='country_pages')

@app.route('/countryview/<countrycode>')
def country_pages(countrycode):
    return render_template('CountryPages.html', 
                            listitems=session.query(Categories).filter(Categories.countrycode==countrycode).all(), 
                            country_info=session.query(Country).filter(Country.code==countrycode).first(),
                            link_to='country_domain')

@app.route('/dataview/<countrycode>/<domain>')
def country_domain(countrycode,domain):
    countrydata = session.query(Series).filter(Series.countrycode==countrycode,Series.categorycode==domain)
    country_info = session.query(Country).filter(Country.code==countrycode).first()
    category_info = session.query(Categories).filter(Categories.countrycode==countrycode, Categories.categorycode==domain).first()
    return render_template('CountryDomains.html', country_info=country_info, country=countrydata, category_info=category_info)

@app.route("/report")
def report():
    return render_template('report.html', countries=session.query(Country).order_by(Country.name).all())

@app.route('/reportview/<countrycode>')
def country_report(countrycode):
    #TODO clean this up
    country = session.query(Country).filter(Country.code==countrycode).first()
    datadomains = session.query(Categories).filter(Categories.countrycode==countrycode).all()
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

@app.route("/review")
def review():
    return render_template('home.html', 
                            countries=reviewSession.query(Country).order_by(Country.name).all(),
                            link_to='review_country_pages')

@app.route('/reviewcountryview/<countrycode>')
def review_country_pages(countrycode):
    return render_template('CountryPages.html', 
                            listitems=reviewSession.query(Categories).filter(Categories.countrycode==countrycode).all(), 
                            country_info=reviewSession.query(Country).filter(Country.code==countrycode).first(),
                            link_to='review_country_domain')

@app.route('/reviewdataview/<countrycode>/<domain>')
def review_country_domain(countrycode,domain):
    countrydata = reviewSession.query(Series).filter(Series.countrycode==countrycode,Series.categorycode==domain)
    country_info = reviewSession.query(Country).filter(Country.code==countrycode).first()
    category_info = reviewSession.query(Categories).filter(Categories.countrycode==countrycode, Categories.categorycode==domain).first()
    return render_template('CountryDomains.html', country_info=country_info, country=countrydata, category_info=category_info)

@app.route("/baseline")
def baseline():
    return render_template('home.html', 
                            countries=baselineSession.query(Country).order_by(Country.name).all(),
                            link_to='baseline_country_pages')

@app.route('/baselinecountryview/<countrycode>')
def baseline_country_pages(countrycode):
    return render_template('CountryPages.html', 
                            listitems=baselineSession.query(Categories).filter(Categories.countrycode==countrycode).all(), 
                            country_info=baselineSession.query(Country).filter(Country.code==countrycode).first(),
                            link_to='baseline_country_domain')

@app.route('/baselinedataview/<countrycode>/<domain>')
def baseline_country_domain(countrycode,domain):
    countrydata = baselineSession.query(Series).filter(Series.countrycode==countrycode,Series.categorycode==domain)
    country_info = baselineSession.query(Country).filter(Country.code==countrycode).first()
    category_info = baselineSession.query(Categories).filter(Categories.countrycode==countrycode, Categories.categorycode==domain).first()
    return render_template('CountryDomains.html', country_info=country_info, country=countrydata, category_info=category_info)

@app.teardown_appcontext
def remove_session(*args, **kwargs):
    session.remove()
    reviewSession.remove()
    baselineSession.remove()