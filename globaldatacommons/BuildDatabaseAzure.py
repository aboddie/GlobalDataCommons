from sqlalchemy import create_engine
from sqlalchemy import Index
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import func

from simple_sdmx import append_client_id
from simple_sdmx import SDMXDataFile

from models import Categories
from models import Country
from models import Series


class NSDPDatabase():

    __slots__ = ['dbconnectionstring', 'engine', 'timeout', 'client_ID']

    def __init__(self, dbconnectionstring, timeout=60, client_id=''):
        self.dbconnectionstring = dbconnectionstring
        self.engine = create_engine(self.dbconnectionstring)
        self.timeout = timeout
        self.client_ID = client_id

    def _get_SDMXfile(self, url):
        clean_url = append_client_id(url.strip().replace(' ', '%20'), self.client_ID)
        return SDMXDataFile(clean_url, timeout=self.timeout)

    def sqlconnection(func):
        def wrapper(self, *args, **kwargs):
            DestSession = sessionmaker(self.engine)
            destSession = DestSession()
            func(self, *args, **kwargs, session=destSession)
            destSession.close()
        return wrapper
        
    @sqlconnection
    def ClearDB(self, **kwargs):
        session = kwargs['session']
        session.query(Series).delete()
        session.query(Categories).delete()
        session.query(Country).delete()
        session.commit()

    def BuildDBIndex(self):
        Index('mycountryindex', Series.countrycode).create(self.engine)
        Index('mycategoryindex', Series.categorycode).create(self.engine)

    def _updatecategorydata(self, destSession, category, DSDdict=dict()):
        def _grabmetadata(series, metadatafield):  # TODO: drop this
            return series.metadata.get(metadatafield, "MISSING DIMISION")
        try:
            category.lastupdated = func.now()
            SDMXfile = self._get_SDMXfile(category.url)
            category.sdmx_version = SDMXfile.version
            category.structure_signiture = f'{SDMXfile.dsd}'
            dsd_url = SDMXfile.dsd.generate_url()
            if dsd_url not in DSDdict:
                DSDdict[dsd_url] = SDMXfile.generate_dsd()
            dsd = DSDdict[dsd_url]
            category.dsd = dsd.name
            for currentseries in SDMXfile.series:
                # TODO: fix check around unit mult
                try:
                    unit_mult = int(_grabmetadata(currentseries, 'UNIT_MULT'))
                except ValueError:
                    raise ValueError("Contains non-integer unit_mult!")
                metadata_names = dsd.name_from_metadata(currentseries)
                metadata_codes = currentseries.metadata
                meta = dict()
                indicatorlist = list()
                for k in metadata_names.keys():
                    meta[k] = (metadata_codes.get(k, ''), metadata_names[k])
                    indicatorlist.append(metadata_codes.get(k, ''))
                for k in metadata_codes.keys():
                    if k not in meta:
                        meta[k] = (metadata_codes[k], '')
                meta = list(meta.items())
                destSession.add(Series(
                        countrycode=category.countrycode,
                        categorycode=category.categorycode,
                        dsd=dsd.name,  # TODO: Remove from model
                        indicator_code='.'.join(indicatorlist),
                        inECOFIN=dsd.validate_series(currentseries),  # TODO: rename
                        indent=0,  # TODO: Remove from model
                        sdmx_data=str(list(currentseries.data.values())),
                        dates=str(currentseries.time_period_coverage),
                        freq=_grabmetadata(currentseries, 'FREQ'), # TODO: Remove from model
                        unit_mult=unit_mult,
                        fieldnames=str([x for (x, y) in meta]),
                        fieldcodes=str([y[0] for (x, y) in meta]),
                        fielddescriptors=str([y[1] for (x, y) in meta]),
                        indicator_description=dsd.name_from_metadata(currentseries).get('INDICATOR', "Invalid code"),  # TODO: Remove from model
                        zero_series=not currentseries.has_nonzero_data,
                        latestdata=currentseries.last_observation))   # TODO: Remove from model
            category.has_error = False
            category.error_text = ''
        except Exception as h:
            category.has_error = True
            category.error_text = str(h)[:245]
            raise h
        finally:
            destSession.commit()

    @sqlconnection
    def UpdateAllData(self, DSDdict=dict(), **kwargs):
        session = kwargs['session']
        session.query(Series).delete()
        session.commit()
        for category in session.query(Categories):
            try:
                self._updatecategorydata(session, category, DSDdict)
            except Exception as h:
                print(f'{category.countrycode} {category.categorycode} {h}')

    @sqlconnection
    def NewCountry(self, name, code, countrystandard, nsdp_url, **kwargs):
        session = kwargs['session']
        querycount = session.query(func.count()).filter(Country.code == code).scalar()
        if querycount == 0:
            session.add
            newCountry = Country(
                    code=code,
                    name=name,
                    countrystandard=countrystandard,
                    nsdp_url=nsdp_url)
            session.add(newCountry)
            session.commit()
        else:
            print("Country code already exists")

    @sqlconnection
    def UpdateCountry(self, countrycode, DSDdict=dict(), **kwargs):
        session = kwargs['session']
        session.query(Series).filter(
                    Series.countrycode == countrycode).delete()
        session.commit()
        for category in session.query(Categories).filter(Categories.countrycode == countrycode):
            try:
                self._updatecategorydata(session, category, DSDdict)
            except Exception as h:
                print(f'{category.countrycode} {category.categorycode} {h}')

    @sqlconnection
    def DeleteCountry(self, countrycode, **kwargs):
        session = kwargs['session']
        session.query(Series).filter(
                    Series.countrycode == countrycode).delete()
        session.query(Categories).filter(
                    Categories.countrycode == countrycode).delete()
        session.query(Country).filter(
                    Country.code == countrycode).delete()
        session.commit()

    @sqlconnection
    def NewCategory(self, countrycode, description, categorycode, url, **kwargs):
        session = kwargs['session']
        querycount = session.query(func.count()).filter(
                Categories.categorycode == categorycode,
                Categories.countrycode == countrycode).scalar()
        if querycount == 0:
            session.add
            newCategory = Categories(
                    countrycode=countrycode,
                    description=description,
                    categorycode=categorycode,
                    url=url)
            session.add(newCategory)
            session.commit()
        else:
            print("Category already exists")

    @sqlconnection
    def UpdateCategory(self, countrycode, categorycode, DSDdict=dict(), **kwargs):
        session = kwargs['session']
        session.query(Series).filter(
                    Series.categorycode == categorycode,
                    Series.countrycode == countrycode).delete()
        session.commit()
        for category in session.query(Categories).filter(Categories.categorycode == categorycode, 
                                                         Categories.countrycode == countrycode):
            try:
                self._updatecategorydata(session, category, DSDdict)
            except Exception as h:
                print(f'{countrycode} {categorycode} {h}')

    @sqlconnection
    def UpdateCategoryURL(self, countrycode, categorycode, newurl, **kwargs):
        session = kwargs['session']
        query = session.query(Categories).filter(
                    Categories.categorycode == categorycode,
                    Categories.countrycode == countrycode)
        if query.count() == 1:
            for category in query:
                category.url = newurl
                session.commit()
        else:
            print('More than one match')

    @sqlconnection
    def UpdateCategoryDescription(self, countrycode, categorycode, newdescription, **kwargs):
        session = kwargs['session']
        query = session.query(Categories).filter(
                    Categories.categorycode == categorycode,
                    Categories.countrycode == countrycode)
        if query.count() == 1:
            for category in query:
                category.description = newdescription
                session.commit()
        else:
            print('More than one match')


    @sqlconnection
    def DeleteCategory(self, countrycode, categorycode, **kwargs):
        session = kwargs['session']
        session.query(Series).filter(
                    Series.categorycode == categorycode,
                    Series.countrycode == countrycode).delete()
        session.query(Categories).filter(
                    Categories.categorycode == categorycode,
                    Categories.countrycode == countrycode).delete()        
        session.commit()

    @sqlconnection
    def UpdateCount(self, **kwargs):
        session = kwargs['session']
        # Category Counts
        seriespercat = session.query(Series.countrycode, Series.categorycode, func.count()).group_by(Series.categorycode, Series.countrycode).all()
        seriespercat = dict([((a, b), c) for (a, b, c) in seriespercat])
        readablepercat = session.query(Series.countrycode, Series.categorycode, func.count()).filter(Series.inECOFIN == True).group_by(Series.categorycode, Series.countrycode).all()
        readablepercat = dict([((a, b), c) for (a, b, c) in readablepercat])
        for category in session.query(Categories):
            category.series_count = seriespercat.get((category.countrycode, category.categorycode), 0)
            category.readable_series = readablepercat.get((category.countrycode, category.categorycode), 0)
        session.commit()
        # Country Counts
        seriespercountry = dict(session.query(Categories.countrycode, func.sum(Categories.series_count)).group_by(Categories.countrycode).all())
        country_has_error = dict(session.query(Categories.countrycode, func.count()).filter(Categories.has_error == True).group_by(Categories.countrycode).all())
        for country in session.query(Country):
            country.series_count = seriespercountry.get(country.code, 0)
            country.has_category_error = bool(country_has_error.get(country.code, 0))
        session.commit()

    @sqlconnection
    def TestConnections(self, start_id=0, **kwargs):
        session = kwargs['session']
        DSDdict = dict()
        for category in session.query(Categories).filter(Categories.has_error == False,
                                                         Categories.id > start_id):
            try:
                self._get_SDMXfile(category.url)
                session.query(Series).filter(Series.categorycode==category.categorycode,
                                             Series.countrycode==category.countrycode).delete()
                session.commit()
                try:
                    self._updatecategorydata(session, category, DSDdict)
                except Exception as h:
                    print(f'{category.countrycode} {category.categorycode} {h}')
            except Exception as h:
                print(f"Test: Can't Connect to: {category.countrycode} {category.categorycode} {h}")

    @staticmethod
    def _find_dup_helper(duplicate_query):
        from ast import literal_eval
        data_dict = dict()
        for dup_series in duplicate_query:
            dates = literal_eval(dup_series.dates)
            data = literal_eval(dup_series.sdmx_data)
            for date, observation in zip(dates, data):
                if date in data_dict:
                    raise Exception('Data overlaps.')
                else:
                    data_dict[date] = observation
        return data_dict

    @sqlconnection
    def find_dup(self, **kwargs):
        # TODO: clean up maybe delete
        # just check indicator codes, if category country and indicator codes all same it is a duplicat
        # if loop over all categories and count duplicate indicator codes
        # if dup if dates don't overlap and all metadata fields the same the a valid duple otherwise an error
        # flag at category level maybe.
        session = kwargs['session']
        stmt = '''select * from
        (select count(countrycode) as mycount, indicator_code, categorycode, countrycode
        from Series where countrycode = 'SVN'
        group by Series.indicator_code,Series.categorycode,Series.countrycode)x
        where mycount > 1'''
        z = session.execute(stmt).fetchall()
        catwithdup = []
        for duplicate in z:
            #indicator_code = duplicate[1]
            categorycode = duplicate[2]
            countrycode = duplicate[3]
            catwithdup.append((countrycode, categorycode))
            #duplicate_query = destSession.query(Series).filter(Series.indicator_code == indicator_code, Series.categorycode == categorycode, Series.countrycode == countrycode)
    #        try:
    #            #print(_find_dup_helper(duplicate_query))
    #            #for dup_series in duplicate_query:
    #            #    print(dup_series.dates)
    #            print(f'{countrycode} {categorycode} {indicator_code}')
    #            print('--'*10)
    #        except:
    #            pass
        print(set(catwithdup))


if __name__ == '__main__':
    import os
    client_id = os.environ['CLIENT_ID']
    Prod = NSDPDatabase(os.environ['SQLAZURECONNSTR_GDC_database'],
                        client_id=client_id)
#    Baseline = NSDPDatabase(os.environ['SQLAZURECONNSTR_GDC_database_baseline']
#                            client_id=client_id)


    Prod.UpdateCategory('FJI','CPI00')

    #Prod.UpdateCountry('LUX')

    #Prod.TestConnections(start_id=1836)

    Prod.UpdateCount()
