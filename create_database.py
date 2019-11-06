from sqlalchemy import *
from sqlalchemy import create_engine, ForeignKey, engine
from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref, sessionmaker

engine = create_engine(
        engine.url.URL(
            drivername='postgres+pg8000',
            username='anderle_michal',
            password='tajneheslo',
            database='binarysearch-database',
            query={
            'unix_sock': '/cloudsql/{}/.s.PGSQL.5432'.format('kocurkovo:europe-west1:binarysearch-database')
            }
            ),
)

#engine = create_engine('sqlite:///database.db', echo=True)
Base = declarative_base()

########################################################################
class User(Base):
	__tablename__ = 'users'

	id = Column(Integer, primary_key = True)
	username = Column(String)
	password = Column(String)

#----------------------------------------------------------------------
	def __init__(self, username, password):
		self.username = username
		self.password = password


class Submit(Base):
	__tablename__ = 'submits'

	id = Column(Integer, primary_key = True)
	user_id = Column(Integer)
	guess = Column(Integer)
	result = Column(Integer)
	time = Column(DateTime)
	attempt = Column(Integer)
	level = Column(Integer)

	def __init__(self, user_id, guess, result, time, attempt, level):
		self.user_id = user_id
		self.guess = guess
		self.result = result
		self.time = time
		self.attempt = attempt
		self.level = level

class Attempt(Base):
	__tablename__ = 'attempts'

	id = Column(Integer, primary_key = True)
	user_id = Column(Integer)
	level = Column(Integer)
	number_of_attempts = Column(Integer)
	best_result = Column(Integer)

	def __init__(self, user_id, level):
		self.user_id = user_id
		self.level = level
		self.number_of_attempts = 0
		self.best_result = -1

# create tables
Base.metadata.create_all(engine)
