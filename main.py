from flask import Flask, render_template, redirect, url_for, request, session, flash
import os
from sqlalchemy.orm import sessionmaker
from create_database import *
from datetime import datetime
from random import randrange
from copy import deepcopy
from get_cat import get_cat

app = Flask(__name__)
app.secret_key = 'admin'

@app.route('/')
def index():
   if 'user_id' not in session:
      return redirect(url_for('login'))
   return render_template('index.html', user = session['user'], results = session['best_results'])

@app.route('/login', methods = ['POST', 'GET'])
def login():
   engine = create_engine('sqlite:///database.db', echo = True)
   if request.method == 'POST':
      DBSession = sessionmaker(bind = engine)
      database_session = DBSession()
      query = database_session.query(User).filter(User.username.in_([request.form['user']]), User.password.in_([request.form['password']]))
      user = query.first()
      # login user
      if user:
         session['user_id'] = user.id
         session['user'] = user.username
         # process attempts
         attempts = database_session.query(Attempt).filter(Attempt.user_id == user.id)
         if not attempts.first():
            for i in range(3):
               database_session.add(Attempt(user.id, i))
            database_session.commit()
            attempts = database_session.query(Attempt).filter(Attempt.user_id == user.id)
         for i in range(3):
            if 'freeze' + str(i) in session:
               session.pop('freeze' + str(i), None)
         session['attempts'] = [0]*3
         session['best_results'] = [0]*3
         for attempt in attempts:
            session['attempts'][attempt.level] = attempt.number_of_attempts
            session['best_results'][attempt.level] = attempt.best_result
         # load previous guesses for current attempt
         session['previous_guesses'] = [[], [], []]
         for i in range(3):
            submits = database_session.query(Submit).filter(Submit.user_id == user.id).filter(Submit.attempt == session['attempts'][i]).filter(Submit.level == i).order_by(Submit.time.desc())
            for submit in submits:
               session['previous_guesses'][i].append((submit.guess, submit.result))
      return redirect(url_for('index'))
   return render_template('login.html')

@app.route('/logout')
def logout():
   session.pop('user_id', None)
   session.pop('user', None)
   session.pop('previous_guesses', None)
   return redirect(url_for('index'))

@app.route('/reset_attempt/<int:level>')
def reset_attempt(level):
   engine = create_engine('sqlite:///database.db', echo = True)
   DBSession = sessionmaker(bind = engine)
   database_session = DBSession()
   db_attempt = database_session.query(Attempt).filter(Attempt.user_id == session['user_id']).filter(Attempt.level == level).first()
   session['previous_guesses'][level] = []
   session.pop('freeze' + str(level), None)
   session['attempts'][level] += 1
   db_attempt.number_of_attempts = session['attempts'][level]
   database_session.commit()
   session.modified = True
   return redirect(url_for('level' + str(level)))

def successful_attempt(level, result):
   engine = create_engine('sqlite:///database.db', echo = True)
   session['best_results'][level] = result if session['best_results'][level] == -1 else min(session['best_results'][level], result)
   DBSession = sessionmaker(bind = engine)
   database_session = DBSession()
   db_attempt = database_session.query(Attempt).filter(Attempt.user_id == session['user_id']).filter(Attempt.level == level).first()
   db_attempt.best_result = session['best_results'][level]
   database_session.commit()
   session.modified = True

SIZE_0 = 100
RANGE_0 = 10000
RESULT_0 = 1000

def get_number_from_interval(beg, end, guess):
   if end[1] < beg[1]:
      beg, end = (beg[0], end[1]), (end[0], beg[1])
      guess = end[0] - (guess - beg[0])
   values = end[1] - beg[1]
   count = end[0] - beg[0] + 1
   step = values//count
   return beg[1] + step*(guess - beg[0]) + randrange(-step//10, step//10)

def get_answer_level0(previous_guesses, guess):
   previous_guesses.append((0, 0))
   previous_guesses.append((SIZE_0 + 1, RANGE_0 + 1))
   previous_guesses.sort()
   for i in range(len(previous_guesses) - 1):
      if previous_guesses[i][1] < RESULT_0 and RESULT_0 < previous_guesses[i+1][1]:
         if abs(guess - previous_guesses[i][0]) < abs(guess - previous_guesses[i+1][0]):
            previous_guesses.append((previous_guesses[i+1][0] - 1, RESULT_0))
         else:
            previous_guesses.append((previous_guesses[i][0] + 1, RESULT_0))
   previous_guesses.sort()
   for i in range(len(previous_guesses) - 1):
      if previous_guesses[i][0] == guess:
         return previous_guesses[i][1]
      if previous_guesses[i][0] < guess and guess < previous_guesses[i+1][0]:
         return get_number_from_interval(previous_guesses[i], previous_guesses[i+1], guess)

def validate_level0(guess):
   if len(str(guess)) == 0 or int(guess) < 1 or int(guess) > SIZE_0:
      flash('Zadana hodnota nebola z rozsahu 1 az %s' % SIZE_0, 'danger')
      return False
   return True

@app.route('/level0', methods = ['POST', 'GET'])
def level0():
   engine = create_engine('sqlite:///database.db', echo = True)
   previous_guesses = session['previous_guesses'][0]
   
   if request.method == 'POST':
      if validate_level0(request.form['value']) and not 'freeze0' in session:
         guess = int(request.form['value'])
         DBSession = sessionmaker(bind = engine)
         database_session = DBSession()
         answer = get_answer_level0(deepcopy(previous_guesses), guess)
         database_session.add(Submit(session['user_id'], guess, answer, datetime.now(), session['attempts'][0], 0))
         database_session.commit()
         previous_guesses = [(guess, answer)] + previous_guesses
         session['previous_guesses'][0] = previous_guesses
         session.modified = True
         if answer == RESULT_0:
            session['freeze0'] = True
            flash('Super! Nasiel si hladane cislo na %s pokusov' % len(previous_guesses), 'success')
            successful_attempt(0, len(previous_guesses))
      elif 'freeze0' in session:
         flash('Uz si nasiel riesenie, ak chces hrat znova, restartuj hru.', 'warning')
   
   return render_template('level0.html', last_guess = -1 if len(previous_guesses) == 0 else previous_guesses[0], guesses = previous_guesses,
                           attempt = session['attempts'][0], user = session['user'], best_result = session['best_results'][0],
                           cat_link = get_cat(), location = RESULT_0)

SIZE_1 = 1000
RANGE_1 = 100000
RESULT_1 = 10000

def get_answer_level1(previous_guesses, guess):
   previous_guesses.append((0, 0))
   previous_guesses.append((SIZE_1 + 1, RANGE_1 + 1))
   previous_guesses.sort()
   for i in range(len(previous_guesses) - 1):
      if previous_guesses[i][1] < RESULT_1 and RESULT_1 < previous_guesses[i+1][1]:
         if abs(guess - previous_guesses[i][0]) < abs(guess - previous_guesses[i+1][0]):
            previous_guesses.append((previous_guesses[i+1][0] - 1, RESULT_1))
         else:
            previous_guesses.append((previous_guesses[i][0] + 1, RESULT_1))
   previous_guesses.sort()
   for i in range(len(previous_guesses) - 1):
      if previous_guesses[i][0] == guess:
         return previous_guesses[i][1]
      if previous_guesses[i][0] < guess and guess < previous_guesses[i+1][0]:
         return get_number_from_interval(previous_guesses[i], previous_guesses[i+1], guess)

def validate_level1(guess):
   if len(str(guess)) == 0 or int(guess) < 1 or int(guess) > SIZE_1:
      flash('Zadana hodnota nebola z rozsahu 1 az %s' % SIZE_1, 'danger')
      return False
   return True

@app.route('/level1', methods = ['POST', 'GET'])
def level1():
   engine = create_engine('sqlite:///database.db', echo = True)
   previous_guesses = session['previous_guesses'][1]
   
   if request.method == 'POST':
      if validate_level1(request.form['value']) and not 'freeze1' in session:
         guess = int(request.form['value'])
         DBSession = sessionmaker(bind = engine)
         database_session = DBSession()
         answer = get_answer_level1(deepcopy(previous_guesses), guess)
         database_session.add(Submit(session['user_id'], guess, answer, datetime.now(), session['attempts'][1], 1))
         database_session.commit()
         previous_guesses = [(guess, answer)] + previous_guesses
         session['previous_guesses'][1] = previous_guesses
         session.modified = True
         if answer == RESULT_1:
            session['freeze1'] = True
            flash('Super! Nasiel si hladane cislo na %s pokusov' % len(previous_guesses), 'success')
            successful_attempt(1, len(previous_guesses))
      elif 'freeze1' in session:
         flash('Uz si nasiel riesenie, ak chces hrat znova, restartuj hru.', 'warning')
   
   return render_template('level1.html', last_guess = -1 if len(previous_guesses) == 0 else previous_guesses[0], guesses = previous_guesses,
                           attempt = session['attempts'][1], user = session['user'], best_result = session['best_results'][1],
                           cat_link = get_cat(), location = RESULT_1)

SIZE_2 = 100
RESULT_2 = 10000

def get_number_at_least(beg, end, guess):
   if end[0] - beg[0] == 2:
      return RESULT_2
   maxi = max(beg[1], end[1])
   step = (RESULT_2 - maxi) // (end[0] - beg[0])
   return RESULT_2 - step * max((end[0] - guess), (guess - beg[0]))

def get_answer_level2(previous_guesses, guess):
   previous_guesses.append((-1, -1))
   previous_guesses.append((0, 0))
   previous_guesses.append((SIZE_2, -1))
   previous_guesses.sort()
   max_pos = 0
   for i in range(len(previous_guesses)):
      if previous_guesses[i][1] > previous_guesses[max_pos][1]:
         max_pos = i
   for i in range(1, len(previous_guesses)):
      if previous_guesses[i][0] == guess:
         return previous_guesses[i][1]
      if previous_guesses[i-1][0] < guess and guess < previous_guesses[i][0]:
         if i-1 == max_pos:
            left = guess - previous_guesses[i-2][0]
            right = previous_guesses[i][0] - previous_guesses[i-1][0]
            if left > right:
               return get_number_from_interval(previous_guesses[i-1], previous_guesses[i], guess)
            else:
               return get_number_at_least(previous_guesses[i-1], previous_guesses[i], guess)
         elif i == max_pos:
            left = previous_guesses[i][0] - previous_guesses[i-1][0]
            right = previous_guesses[i+1][0] - guess
            if right > left:
               return get_number_from_interval(previous_guesses[i-1], previous_guesses[i], guess)
            else:
               return get_number_at_least(previous_guesses[i-1], previous_guesses[i], guess)
         else:
            return get_number_from_interval(previous_guesses[i-1], previous_guesses[i], guess)

def validate_level2(guess):
   if len(str(guess)) == 0 or int(guess) < 1 or int(guess) > SIZE_2:
      flash('Zadana hodnota nebola z rozsahu 1 az %s' % SIZE_2, 'danger')
      return False
   return True

@app.route('/level2', methods = ['POST', 'GET'])
def level2():
   engine = create_engine('sqlite:///database.db', echo = True)
   previous_guesses = session['previous_guesses'][2]
   
   if request.method == 'POST':
      if validate_level2(request.form['value']) and not 'freeze2' in session:
         guess = int(request.form['value'])
         DBSession = sessionmaker(bind = engine)
         database_session = DBSession()
         answer = get_answer_level2(deepcopy(previous_guesses), guess)
         database_session.add(Submit(session['user_id'], guess, answer, datetime.now(), session['attempts'][2], 2))
         database_session.commit()
         previous_guesses = [(guess, answer)] + previous_guesses
         session['previous_guesses'][2] = previous_guesses
         session.modified = True
         if answer == RESULT_2:
            session['freeze2'] = True
            flash('Super! Nasiel si hladane cislo na %s pokusov' % len(previous_guesses), 'success')
            successful_attempt(2, len(previous_guesses))
      elif 'freeze2' in session:
         flash('Uz si nasiel riesenie, ak chces hrat znova, restartuj hru.', 'warning')
   
   return render_template('level2.html', last_guess = -1 if len(previous_guesses) == 0 else previous_guesses[0], guesses = previous_guesses,
                           attempt = session['attempts'][2], user = session['user'], best_result = session['best_results'][2],
                           cat_link = get_cat(), location = RESULT_2)

if __name__ == '__main__':
   app.run(port = 8080, debug = True)
