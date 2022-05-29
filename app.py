from pprint import pprint
import sqlite3
import re

from flask import Flask, url_for, request, render_template, redirect, jsonify, session
from flask_cors import CORS
from random import randrange as rr

app = Flask(__name__)
CORS(app)
app.secret_key = 'hello'


def db_connection():
    conn = None
    try:
        conn = sqlite3.connect(f'Users.sqlite')
    except Exception as e:
        print(e)
    return conn


@app.route('/')
def base():
    return render_template('Home.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if 'username' in session:
        redirect(url_for('status'))

    if request.method != 'POST':
        return render_template('Login.html', error=error)

    data = request.form

    username = data['user-username']
    password = data['user-password']

    con = db_connection()
    cursor = con.cursor()
    query = f"SELECT username, password FROM Users WHERE username = (?) and password = (?);"
    cursor.execute(query, (username, password))
    db_reply = cursor.fetchone()
    con.close()

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

    con = db_connection()
    cursor = con.cursor()
    query = f"SELECT username FROM Users WHERE username = (?) ;"
    cursor.execute(query, (data['username'],))
    db_reply = cursor.fetchone()

    if db_reply is not None:
        error = "user already exists"
        cursor.close()
        con.close()
        return render_template('Register.html', error=error)

    if not bool(re.match("[+]7[0-9]{10}", phone)):
        error = "incorrect phone pattern, it should be +7xxxxxxxx"
        return render_template('Register.html', error=error)

    query = f"INSERT INTO Users (username, password, email, address, phone) " \
            f"VALUES(?, ?, ?, ?, ?);"

    try:
        cursor.execute(query, (username, password, email, address, phone))
        con.commit()
    except Exception as e:
        cursor.close()
        con.close()
        error = e
        return render_template('Register.html', error=error)

    session['username'] = username
    return redirect(url_for('status'))


@app.route('/logout')
def logout():
    if 'username' in session:
        session.pop('username')
        return redirect(url_for('login'))
    redirect(url_for('login'))


@app.route("/user/Status")
def status():
    error = None

    if 'username' not in session:
        redirect(url_for('login'))

    username = session['username']

    query = f"SELECT house_name, structure_type, sensor_type FROM Houses WHERE username = (?)"

    con = db_connection()
    cursor = con.cursor()
    cursor.execute(query, (username,))
    db_reply = cursor.fetchall()
    cursor.close()
    con.close()

    data_ = {}
    for row in db_reply:

        elements = [elem for elem in row]

        root = elements[0]
        structure = elements[1]
        sensor = elements[2]

        if root not in data_:
            data_[root] = {structure: {sensor: rr(0, 100)}}
            continue

        if structure not in data_[root]:
            data_[root][structure] = {sensor: rr(0, 100)}
            continue

        if sensor not in data_[root][structure]:
            data_[root][structure][sensor] = rr(0, 100)

    data = {k: data_[k] for k in sorted(data_)}

    return render_template('Status.html', user=username, error=error, stats=data)


@app.route("/user/Settings", methods=['GET', 'POST'])
def settings():
    error = None

    if "username" not in session:
        error = "Not authorized"
        redirect(url_for('login', error=error))

    username = session['username']

    query = f"SELECT house_name, structure_type, sensor_type, sensor_ui_value FROM Houses WHERE username = (?)"

    con = db_connection()
    cursor = con.cursor()
    cursor.execute(query, (username,))
    db_reply = cursor.fetchall()
    cursor.close()
    con.close()

    data_ = {}
    for row in db_reply:

        elements = [elem for elem in row]
        root = elements[0]
        structure = elements[1]
        sensor = elements[2]
        value = elements[3]

        if root not in data_:
            data_[root] = {structure: {sensor: value}}
            continue

        if structure not in data_[root]:
            data_[root][structure] = {sensor: value}
            continue

        if sensor not in data_[root][structure]:
            data_[root][structure][sensor] = value

        if sensor not in data_[root][structure]:
            data_[root][structure][sensor] = value

    data = {k: data_[k] for k in sorted(data_)}

    if request.method == "POST":
        form_data = request.form
        ui_settings = {}
        for param, value in form_data.items():
            if value != "":
                ui_settings[param] = value

        for settings in ui_settings:
            path = settings.split(".")
            house_name = path[0]
            structure_name = path[1]
            sensor_name = path[2]
            value = ui_settings[settings]

            query = f"update Houses set " \
                    f"sensor_ui_value = '{value}' " \
                    f"where " \
                    f"house_name = '{house_name}' and " \
                    f"structure_type = '{structure_name}' and " \
                    f"sensor_type = '{sensor_name}' and " \
                    f"username = '{username}';"

            con = db_connection()
            cursor = con.cursor()

            try:
                cursor.execute(query)
                con.commit()
                cursor.close()
                con.close()
                return redirect(url_for('settings'))
            except Exception as e:
                cursor.close()
                con.close()
                error = e
                return render_template('Settings.html', error=error)

    return render_template('Settings.html', user=session['username'], error=error, data=data)


@app.route("/api/stats")
def gen_data():
    # if 'username' not in session:
    #     return jsonify({})

    username = session['username']

    query = f"SELECT house_name, structure_type, sensor_type FROM Houses " \
            f"WHERE username=(?)"

    con = db_connection()
    cursor = con.cursor()
    cursor.execute(query, (username,))
    db_reply = cursor.fetchall()
    cursor.close()
    con.close()

    data = {}

    for row in db_reply:

        elements = [elem for elem in row]

        root = elements[0]
        structure = elements[1]
        sensor = elements[2]

        if root not in data:
            data[root] = {structure: {sensor: rr(0, 100)}}
            continue

        if structure not in data[root]:
            data[root][structure] = {sensor: rr(0, 100)}
            continue

        if sensor not in data[root][structure]:
            data[root][structure][sensor] = rr(0, 100)

    return jsonify(data)


if __name__ == '__main__':
    app.run(debug=True)
