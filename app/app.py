from typing import List, Dict
import simplejson as json
from flask import Flask, render_template, request, redirect, url_for, session
from flask import render_template
from flaskext.mysql import MySQL
from pymysql.cursors import DictCursor
import hashlib

app = Flask(__name__)
mysql = MySQL(cursorclass=DictCursor)

app.config['MYSQL_DATABASE_HOST'] = 'us-cdbr-east-02.cleardb.com'
app.config['MYSQL_DATABASE_USER'] = 'b8245d5e04777e'
app.config['MYSQL_DATABASE_PASSWORD'] = '1027a2d6'
app.config['MYSQL_DATABASE_PORT'] = 3306
app.config['MYSQL_DATABASE_DB'] = 'heroku_a6d0e70501b6383'
mysql.init_app(app)
message = ''


@app.route('/', methods=['GET'])
def index():
    return render_template('homepage.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    message = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        # Create variables for easy access
        username = request.form['username']
        password = hashlib.md5(request.form['password'].encode(encoding='UTF-8', errors='strict')).hexdigest()
        cursor = mysql.get_db().cursor()
        cursor.execute('SELECT * FROM userTable WHERE username = %s AND password = %s', (username, password,))
        # Fetch one record and return result
        account = cursor.fetchone()
        if account:
            # Create session data, we can access this data in other routes
            # session['id'] = account['id']
            # session['username'] = account['username']
            # Redirect to home page
            message = 'Logged in successfully!'

            return render_template('profile.html', firstname=account['firstname'], lastname=account['lastname'],
                                   school=account['department'], year=account['year'])
        else:
            # Account doesnt exist or username/password incorrect
            message = 'Incorrect username/password!'
    return render_template('login.html', msg=message)


@app.route('/logout', methods=['GET'])
def logout():
    # session.pop('username', None)
    # session.pop('id', None)
    return redirect('/', code=302)


if __name__ == '__main__':
    app.secret_key = 'super secret key'
    app.run()
