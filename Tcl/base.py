# coding=utf-8

# from django.conf import settings
from decouple import config
from sqlalchemy import create_engine

from sqlalchemy.orm import (scoped_session, sessionmaker, relationship,backref)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool

engine = create_engine(config('DATABASE_URL'))
Session = scoped_session(sessionmaker(bind=engine,expire_on_commit=False))
Base = declarative_base()
Base.query = Session.query_property()
