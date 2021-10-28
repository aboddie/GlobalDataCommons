import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from flask import Flask


app = Flask(__name__)
app.jinja_env.trim_blocks = True
app.jinja_env.lstrip_blocks = True

engine = create_engine(os.environ['SQLAZURECONNSTR_GDC_database'])
Session = sessionmaker(engine)

review_engine = create_engine(os.environ['SQLAZURECONNSTR_GDC_database_STG'])
ReviewSession = sessionmaker(review_engine)

from . import routes
