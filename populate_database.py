import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from create_database import *

engine = create_engine('sqlite:///database.db', echo=True)

# create a Session
Session = sessionmaker(bind=engine)
session = Session()

user = User("admin","admin")
session.add(user)

user = User("zaba","zaba")
session.add(user)

user = User("korytnacka","korytnacka")
session.add(user)

# commit the record the database
session.commit()

session.commit()