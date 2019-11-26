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

ovocie = ['jablko', 'hruska', 'ceresna', 'broskyna', 'slivka', 'marhula', 'ringlota', 'cucoriedka', 'brusnica', 'egres', 'hrozno', 'malina',
		  'jahoda', 'morusa', 'gastan', 'pomaranc', 'banan', 'mandarinka', 'ananas', 'citron', 'marakuja', 'avokado', 'datla', 'figa', 'grapefruit',
		  'guave', 'kivi', 'limetka', 'mango', 'marakuja', 'oliva', 'papaja', 'pomelo']

zvierata = ['pes', 'macka', 'vevericka', 'zajac', 'kralik', 'opica', 'uskatec', 'hroch', 'slon', 'zirafa', 'panda', 'orangutan', 'jezko', 'had', 'uzovka', 'chobotnica',
            'sykorka', 'gepard', 'tiger', 'mys', 'plch', 'vlk', 'liska', 'medved', 'jelen', 'srnka', 'dikobraz', 'mravec', 'fenek', 'lev', 'antilopa', 'simpanz', 'kon']

def add_new_users(names):
    Session = sessionmaker(bind=engine)
    session = Session()

    for x in names:
        password = ''
        for i in range(6):
            password = password + get_char()
        print(x, password)
        user = User(x, password)
        session.add(user)

    session.commit()
    session.commit()

add_new_users(zvierata)
