from typing import List, Dict
import simplejson as json
from flask import Flask, render_template, request, redirect, url_for, session
from flask import render_template
from flaskext.mysql import MySQL
from pymysql.cursors import DictCursor
import smtplib, ssl
import hashlib

app = Flask(__name__)
mysql = MySQL(cursorclass=DictCursor)

# app.config['MYSQL_DATABASE_HOST'] = 'us-cdbr-east-02.cleardb.com'
# app.config['MYSQL_DATABASE_USER'] = 'b8245d5e04777e'
# app.config['MYSQL_DATABASE_PASSWORD'] = '1027a2d6'
# app.config['MYSQL_DATABASE_PORT'] = 3306
# app.config['MYSQL_DATABASE_DB'] = 'heroku_a6d0e70501b6383'

app.config['MYSQL_DATABASE_HOST'] = 'db'
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'root'
app.config['MYSQL_DATABASE_PORT'] = 3306
app.config['MYSQL_DATABASE_DB'] = 'userData'
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
        account = cursor.fetchall()
        if account:
            # Create session data, we can access this data in other routes
            # session['id'] = account['id']
            # session['username'] = account['username']
            message = 'Logged in successfully!'
            # print(account['id'])
            user = account[0]
            user_id = int(user['id'])
            return redirect('/profile/{}'.format(user_id))
        else:
            # Account doesnt exist or username/password incorrect
            message = 'Incorrect username/password!'
    return render_template('login.html', msg=message)

@app.route('/profile/<int:user_id>', methods=['GET'])
def profile(user_id):
    cursor = mysql.get_db().cursor()
    cursor.execute('SELECT * FROM userTable WHERE id = %s', (user_id))
    # Fetch one record and return result
    account = cursor.fetchone()
    return render_template('profile.html', firstname=account['firstname'], lastname=account['lastname'],
                           school=account['school'], department=account['department'], year=account['year'],
                           activate=account['isactivate'], id=account['id'])


@app.route('/logout', methods=['GET'])
def logout():
    session.pop('username', None)
    session.pop('id', None)
    return redirect('/', code=302)


@app.route('/register', methods=['GET'])
def register_get():
    message = ''
    return render_template('register.html', msg=message)


@app.route('/register', methods=['POST'])
def register_post():
    message = ''
    cursor = mysql.get_db().cursor()
    username = request.form['username']
    cursor.execute('SELECT * FROM userTable WHERE username = %s', (username))
    account = cursor.fetchone()
    if account:
        message = 'username already exist'
        return render_template('register.html', msg=message)
    if request.form['password'] != request.form['confirm_password']:
        message = 'password is not match'
        return render_template('register.html', msg=message)
    inputData = (request.form.get('username'),
                 hashlib.md5(request.form['password'].encode(encoding='UTF-8', errors='strict')).hexdigest(),
                 request.form.get('firstname'),
                 request.form.get('lastname'), request.form.get('school'),
                 request.form.get('department'), request.form.get('year'), False)
    sql_insert_query = """INSERT INTO userTable (username,password,firstname,lastname,school,department,`year`,isactivate) VALUES (%s, %s,%s, %s,%s, %s,%s,%s) """
    cursor.execute(sql_insert_query, inputData)
    mysql.get_db().commit()
    smtp_server = "smtp.gmail.com"
    port = 587  # For starttls
    sender_email = "is601final@gmail.com"
    receiver_email = request.form.get('username')
    mail_password = 'xudryc-waNfy9-zopfyv'
    main_url = 'https://schoolhub2020.herokuapp.com/'

    content = """\
    Subject: Activate Account to School Hub

    Please click this link to activate: """ + str

    context = ssl.create_default_context()
    # Try to log in to server and send email
    try:
        server = smtplib.SMTP(smtp_server, port)
        server.ehlo()  # Can be omitted
        server.starttls(context=context)  # Secure the connection
        server.ehlo()  # Can be omitted
        server.login(sender_email, mail_password)
        # TODO: Send email here
    except Exception as e:
        # Print any error messages to stdout
        print(e)
    finally:
        server.quit()

    return render_template('profile.html', firstname=request.form.get('firstname'),
                           lastname=request.form.get('lastname'),
                           school=request.form.get('school'), department=request.form.get('department'),
                           year=request.form.get('year'),
                           activate=request.form.get('isactivate'))


if __name__ == '__main__':
    app.secret_key = 'super secret key'
    app.run(host='0.0.0.0')
