from globaldatacommons import db

class Country(db.Model):
    __tablename__ = 'country'
    code = db.Column(db.String(3), primary_key = True, nullable = False)
    name = db.Column(db.String(100), nullable = False)
    series_count = db.Column(db.Integer, default = 0)
    has_category_error = db.Column(db.Boolean, default = False)
    countrystandard = db.Column(db.String(10), nullable = False)
    nsdp_url = db.Column(db.String(250), nullable = True)
    allcategories = db.relationship('Categories', backref='parentcountry')
    
    def __repr__(self):
        return f"Country: {self.name}"

class Categories(db.Model):
    __tablename__ = 'categories'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    countrycode = db.Column(db.String(3), db.ForeignKey('country.code'), nullable = False)
    description = db.Column(db.String(250), nullable = False)
    dsd = db.Column(db.String(250), default = '')
    has_error = db.Column(db.Boolean, default = False) 
    error_text = db.Column(db.String(250), default = '')
    categorycode = db.Column(db.String(10), nullable = False)
    domaincode = db.Column(db.String(10), nullable = False)
    url = db.Column(db.Text, nullable = False)
    series_count = db.Column(db.Integer, default = 0)
    readable_series = db.Column(db.Integer, default = 0)

    
    def __repr__(self):
        return f"Categories: {self.description}"

class Series(db.Model):
    __tablename__ = 'series'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    countrycode = db.Column(db.String(3), db.ForeignKey('country.code'), nullable = False)
    categorycode = db.Column(db.String(10), db.ForeignKey('categories.categorycode'), nullable = False)
    dsd = db.Column(db.String(250), db.ForeignKey('categories.dsd'), nullable = False)
    indicator_code = db.Column(db.String(250), nullable = False)
    inECOFIN = db.Column(db.Boolean, nullable = False)
    indent = db.Column(db.Integer, nullable = False, default = 0)
    freq = db.Column(db.String(1), nullable = False)
    unit_mult = db.Column(db.Integer, nullable = False, default = 0)
    indicator_description = db.Column(db.Text, nullable = False)
    sdmx_data = db.Column(db.Text, nullable = False)
    dates = db.Column(db.Text, nullable = False)
    fieldnames = db.Column(db.Text, nullable = False)
    fieldcodes = db.Column(db.Text, nullable = False)
    fielddescriptors = db.Column(db.Text, nullable = False)
     
    def __repr__(self):
        return f"Series {self.indicator_description}"

