import json
from pprint import pprint
import sqlite3

from flask import Flask, url_for, request, render_template, redirect, jsonify, session, flash
from flask_cors import CORS
from random import randrange as rr

app = Flask(__name__)
CORS(app)
app.secret_key = 'hello'


def db_connection(db_name: str):
    conn = None
    try:
        conn = sqlite3.connect(f'{db_name}.sqlite')
    except sqlite3.error as e:
        print(e)
    return conn


@app.route('/')
def base():
    return render_template('Home.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if session['username'] is not None:
        redirect(url_for('status'))

    if request.method != 'POST':
        return render_template('Login.html', error=error)

    data = request.form
    pprint(data)

    username = data['user-username']
    password = data['user-password']

    conn_users = db_connection('Users')
    cursor = conn_users.cursor()
    query = f"SELECT username, password FROM Users WHERE username='{username}' and password='{password}'"
    cursor.execute(query)
    db_reply = cursor.fetchone()
    print(db_reply)

    if db_reply is None:
        error = "Incorrect username or password"
        return render_template('Login.html', error=error)

    session['username'] = username
    return redirect(url_for('status'))


@app.route('/registration', methods=['GET', 'POST'])
def registration():
    error = None

    if request.method != 'POST':
        return render_template('Register.html', error=error)

    data = request.form

    username = data['username']
    password = data['password']
    email = data['email']
    address = data['address']
    phone = data['phone']
    pprint(data)

    conn_users = db_connection('Users')
    cursor = conn_users.cursor()
    query = f"SELECT username FROM Users WHERE username='{username}'"
    cursor.execute(query)
    db_reply = cursor.fetchone()

    if db_reply is not None:
        error = "user already exists"
        return render_template('Register.html', error=error)

    query = f"INSERT INTO Users (username, password, email, address, phone) " \
            f"VALUES(?, ?, ?, ?, ?);"

    try:
        cursor.execute(query, (username, password, email, address, phone))
        conn_users.commit()
    except Exception as e:
        error = e
        return render_template('Register.html', error=error)

    session['username'] = username
    return redirect(url_for('status'))


@app.route('/logout')
def logout():
    if 'username' in session:
        session['username'].pop()
        return redirect(url_for('base'))
    redirect(url_for('login'))


@app.route("/user/status")
def status():
    return render_template('Status.html')


@app.route("/user/settings")
def settings():
    error = None
    rows = None

    if "username" not in session:
        error = "Not authorized"
        redirect(url_for('login', error=error))

    query = f"SELECT house_name, structure_type, sensor_type, sensor_ui_value FROM Houses WHERE username='{session['username']}'"
    conn_houses = db_connection('Users')
    conn_houses.row_factory = sqlite3.Row
    cursor = conn_houses.cursor()
    cursor.execute(query)

    db_reply = cursor.fetchall()
    keys = ['house_name', 'structure_type', 'sensor_type', 'sensor_ui_value']
    rows_dict = [{keys[idx]: row for idx, row in enumerate(reply)} for reply in db_reply]
    rows = [[row for row in reply] for reply in db_reply]
    print(rows)
    pprint(rows_dict)

    return render_template('Settings.html', error=error, rows=rows_dict)


@app.route("/api/stats")
def gen_data():
    data = {
        'boiler': {
            'temp': rr(0, 1000) / 100,
            'power': rr(0, 1000) / 100,
        },
        'kitchen': {
            'temp': rr(1500, 4000) / 100,
            'humid': rr(0, 1000) / 100,
        },
        'room': {
            'temp': rr(1500, 4000) / 100,
            'humid': rr(0, 1000) / 100,
        }
    }
    return jsonify(data)


if __name__ == '__main__':
    app.run(debug=True)
