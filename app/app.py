from typing import List, Dict
import simplejson as json
from flask import Flask, render_template, request, redirect, url_for, session
from flask import render_template
from flaskext.mysql import MySQL
from pymysql.cursors import DictCursor
import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import hashlib

app = Flask(__name__)
mysql = MySQL(cursorclass=DictCursor)

app.config['MYSQL_DATABASE_HOST'] = 'us-cdbr-east-02.cleardb.com'
app.config['MYSQL_DATABASE_USER'] = 'b90ece5bbd6812'
app.config['MYSQL_DATABASE_PASSWORD'] = 'f5dbc703'
app.config['MYSQL_DATABASE_PORT'] = 3306
app.config['MYSQL_DATABASE_DB'] = 'heroku_d57e0c92f5d3a70'

# app.config['MYSQL_DATABASE_HOST'] = 'db'
# app.config['MYSQL_DATABASE_USER'] = 'root'
# app.config['MYSQL_DATABASE_PASSWORD'] = 'root'
# app.config['MYSQL_DATABASE_PORT'] = 3306
# app.config['MYSQL_DATABASE_DB'] = 'userData'
mysql.init_app(app)


# message = ''


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
    # session.pop('username', None)
    # session.pop('id', None)
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
    username = request.form['username']
    password = hashlib.md5(request.form['password'].encode(encoding='UTF-8', errors='strict')).hexdigest()
    cursor = mysql.get_db().cursor()
    cursor.execute('SELECT * FROM userTable WHERE username = %s AND password = %s', (username, password,))
    account = cursor.fetchall()
    user = account[0]
    user_id = int(user['id'])

    smtp_server = "smtp.gmail.com"
    port = 587  # For starttls
    sender_email = "is601final@gmail.com"
    receiver_email = request.form.get('username')
    mail_password = 'xudryc-waNfy9-zopfyv'
    main_url = 'https://schoolhub2020.herokuapp.com/activate/{}'.format(user_id)

    message = MIMEMultipart("alternative")
    message["Subject"] = "Activating Account for School Hub"
    message["From"] = sender_email
    message["To"] = receiver_email
    content = """\
    Subject: Activate Account to School Hub

    Please click this link to activate: """ + main_url
    part1 = MIMEText(content, "plain")
    message.attach(part1)
    context = ssl.create_default_context()
    # Try to log in to server and send email
    try:
        server = smtplib.SMTP(smtp_server, port)
        server.ehlo()  # Can be omitted
        server.starttls(context=context)  # Secure the connection
        server.ehlo()  # Can be omitted
        server.login(sender_email, mail_password)
        server.sendmail(sender_email, receiver_email, message.as_string())
    except Exception as e:
        # Print any error messages to stdout
        print(e)
    finally:
        server.quit()
    return redirect('/profile/{}'.format(user_id))


@app.route('/activate/<int:user_id>', methods=['GET'])
def activate(user_id):
    cursor = mysql.get_db().cursor()
    cursor.execute('SELECT * FROM userTable WHERE id = %s', (user_id))
    result = cursor.fetchall()
    user = result[0]
    inputData = (user['username'], user['password'], user['firstname'],
                 user['lastname'], user['school'], user['department'], user['year'], True, user_id)
    sql_update_query = """UPDATE userTable t SET t.username = %s, t.password = %s, t.firstname = %s, t.lastname = 
        %s, t.school = %s, t.department = %s, t.year = %s, t.isactivate=%s WHERE t.id = %s """
    cursor.execute(sql_update_query, inputData)
    mysql.get_db().commit()
    return redirect('/profile/{}'.format(user_id))


if __name__ == '__main__':
    app.secret_key = 'super secret key'
    app.run(host='0.0.0.0')
