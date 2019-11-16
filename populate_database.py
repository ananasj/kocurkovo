import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from create_database import *
from random import choice

engine = create_engine('sqlite:///database.db', echo=True)

def get_char():
	znaky = []
	for i in range(26):
		znaky.append(chr(ord('a') + i))
		znaky.append(chr(ord('A') + i))
	for i in range(10):
		znaky.append(chr(ord('0') + i))
	return choice(znaky)

# create a Session
Session = sessionmaker(bind=engine)
session = Session()

user = User("admin","zabaakorytnackarobiavyskum")
session.add(user)

user = User("zaba","zaba")
session.add(user)

user = User("korytnacka","korytnacka")
session.add(user)

ovocie = ['jablko', 'hruska', 'ceresna', 'broskyna', 'slivka', 'marhula', 'ringlota', 'cucoriedka', 'brusnica', 'egres', 'hrozno', 'malina',
		  'jahoda', 'morusa', 'gastan', 'pomaranc', 'banan', 'mandarinka', 'ananas', 'citron', 'marakuja', 'avokado', 'datla', 'figa', 'grapefruit',
		  'guave', 'kivi', 'limetka', 'mango', 'marakuja', 'oliva', 'papaja', 'pomelo']

print(len(ovocie))
for x in ovocie:
	password = ''
	for i in range(6):
		password = password + get_char()
	print(x, password)
	user = User(x, password)
	session.add(user)

# commit the record the database
session.commit()

session.commit()