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

    if request.method == 'POST':

        data = request.form
        pprint(data)

        username = data['user-username']
        password = data['user-password']

        conn_users = db_connection('Users')
        cursor = conn_users.cursor()
        query = f"SELECT username, password FROM Users WHERE username='{username}'"
        cursor.execute(query)
        db_reply = cursor.fetchone()

        if username == 'test' and password == 'test':
            return redirect(url_for('status'))
        else:
            error = "Incorrect username or password"
            return render_template('Login.html', error=error)

    else:
        return render_template('Login.html', error=error)


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
            f"VALUES('{username}', '{password}', '{email}', '{address}', '{phone}');"

    try:
        cursor.execute(query)
    except Exception as e:
        error = e
        return render_template('Register.html', error=error)

    session['username'] = username
    return redirect(url_for('status'))


@app.route('/logout')
def logout():
    session['username'].pop()
    return redirect(url_for('base'))


@app.route("/user/status")
def status():
    return render_template('Status.html')


@app.route("/user/settings")
def settings():
    return render_template('Settings.html')


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
