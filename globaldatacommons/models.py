import sqlalchemy as sa
from sqlalchemy.ext.declarative import declarative_base


metadata_obj = declarative_base()


class Country(metadata_obj):
    """Model for country table."""

    __tablename__ = 'country'
    code = sa.Column(sa.String(3), primary_key=True, nullable=False)
    name = sa.Column(sa.String(100), nullable=False)
    series_count = sa.Column(sa.Integer, default=0)
    has_category_error = sa.Column(sa.Boolean, default=False)
    countrystandard = sa.Column(sa.String(10), nullable=False)
    nsdp_url = sa.Column(sa.String(250), nullable=True)
    allcategories = sa.orm.relationship('Categories')

    def __repr__(self):
        return f"Country: {self.name}"


class Categories(metadata_obj):
    """Model for categories table."""

    __tablename__ = 'categories'
    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    countrycode = sa.Column(sa.String(3), sa.ForeignKey('country.code'), nullable=False)
    categorycode = sa.Column(sa.String(10), nullable=False)
    url = sa.Column(sa.Text, nullable=False)
    description = sa.Column(sa.String(250), nullable=False)
    dsd = sa.Column(sa.String(250), default='')
    structure_signiture = sa.Column(sa.String(250), default='')
    sdmx_version = sa.Column(sa.String(3), default='')
    has_error = sa.Column(sa.Boolean, default=False)
    error_text = sa.Column(sa.String(250), default='')
    series_count = sa.Column(sa.Integer, default=0)
    readable_series = sa.Column(sa.Integer, default=0)
    lastupdated = sa.Column(sa.DateTime(timezone=True))

    def __repr__(self):
        return f"Category: {self.description}"


class Series(metadata_obj):
    """Model for series table."""

    __tablename__ = 'series'
    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    countrycode = sa.Column(sa.String(3), sa.ForeignKey('country.code'), nullable=False)
    categorycode = sa.Column(sa.String(10), nullable=False)
    indicator_code = sa.Column(sa.String(250), nullable=False)
    validcodes = sa.Column(sa.Boolean, nullable=False)
    unit_mult = sa.Column(sa.Integer, nullable=False, default=0)
    indicator_description = sa.Column(sa.Text, nullable=False)
    sdmx_data = sa.Column(sa.Text, nullable=False)
    dates = sa.Column(sa.Text, nullable=False)
    fieldnames = sa.Column(sa.Text, nullable=False)
    fieldcodes = sa.Column(sa.Text, nullable=False)
    fielddescriptors = sa.Column(sa.Text, nullable=False)
    zero_series = sa.Column(sa.Boolean, nullable=False)

    def __repr__(self):
        return f"Series: {self.indicator_description}"
