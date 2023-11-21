import flask
from flask import Flask, render_template, url_for, request, session, redirect

import sqlite3
import random
import dbController
import hashlib
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = 'o1234k124gku124g12'

menu = [{'name': 'Авторизация', 'url': '/log'},
        {'name': 'Регистрация', 'url': '/reg'},
        {'name': 'Главная', 'url': '/'}]


@app.route("/", methods=["POST", "GET"])
def index():
    conn = sqlite3.connect('db.db')
    cur = conn.cursor()
    ms = []
    baselink = request.base_url
    baselink = baselink[:-5]
    typeln = cur.execute('SELECT * FROM links_types').fetchall()
    publicln = cur.execute('SELECT * FROM `links` INNER JOIN links_types ON links_types.id = links.link_type_id WHERE links_types.type = "general"').fetchall()
    if session.get('userLogged') != None:
        user_id = cur.execute('SELECT "id" FROM users WHERE login = ?', (session.get('userLogged'),)).fetchone()
        id1 = user_id[0]
        ms = cur.execute(
            'SELECT * FROM links INNER JOIN links_types ON links_types.id = links.link_type_id  WHERE user_id = ?',
            (id1,)).fetchall()
        menu = [{'name': 'Выйти', 'url': '/logout'},
                {'name': session.get('userLogged'), 'url': '/log'}]
        if request.method == 'POST':
            ms = cur.execute(
                'SELECT * FROM links INNER JOIN links_types ON links_types.id = links.link_type_id  WHERE user_id = ?',
                (id1,)).fetchall()
            hreflink = request.form['hreflink']
            if hreflink == [] or hreflink == '':
                user_adress = hashlib.md5(request.form['link'].encode()).hexdigest()[:random.randint(8, 12)]
                ln = request.form['link']
                type1 = request.form['type']
                name = session.get('userLogged')
                # pyperclip.copy(kopy)
                user_id = cur.execute('SELECT "id" FROM users WHERE login = ?', (session.get('userLogged'),)).fetchone()
                id1 = user_id[0]

                cur.execute('''INSERT INTO links('link','hreflink', 'user_id', 'link_type_id') VALUES(?, ?, ?, ?)''', (ln, user_adress,id1, type1))
                conn.commit()
                ms = cur.execute(
                    'SELECT * FROM links INNER JOIN links_types ON links_types.id = links.link_type_id  WHERE user_id = ?',
                    (id1,)).fetchall()
                print(ms)
                flask.flash(f'{user_adress}')
            else:
                ln = request.form['link']
                type1 = request.form['type']
                name = session.get('userLogged')
                # pyperclip.copy(kopy)
                hreflink = request.form['hreflink']
                user_id = cur.execute('SELECT "id" FROM users WHERE login = ?', (session.get('userLogged'),)).fetchone()
                id1 = user_id[0]
                cur.execute('''INSERT INTO links('link','hreflink', 'user_id', 'link_type_id') VALUES(?, ?, ?, ?)''', (ln, hreflink,id1, type1))
                conn.commit()
                flask.flash(f'{hreflink}')
                ms = cur.execute(
                    'SELECT * FROM links INNER JOIN links_types ON links_types.id = links.link_type_id  WHERE user_id = ?',
                    (id1,)).fetchall()
                # print(request.form['link'])
                # print(name)

                print(ms)

    else:
        menu = [{'name': 'Авторизация', 'url': '/log'},
                {'name': 'Регистрация', 'url': '/reg'},
                {'name': 'Главная', 'url': '/'}]
        if request.method == 'POST':
            user_adress = hashlib.md5(request.form['link'].encode()).hexdigest()[:random.randint(8, 12)]
            ln = request.form['link']
            type1 = request.form['type']
            name = session.get('userLogged')
            # pyperclip.copy(kopy)
            cur.execute('''INSERT INTO links('link','hreflink', 'user_id', 'link_type_id') VALUES(?, ?, Null, ?)''', (ln, user_adress, type1))
            conn.commit()
            user_adress = hashlib.md5(request.form['link'].encode()).hexdigest()[:random.randint(8, 12)]
            print(user_adress)
            print(baselink)
            print(request.form['link'])
            # print(request.form['type'])
            # print(ski)
            href = cur.execute(
                '''SELECT * FROM links INNER JOIN links_types ON links_types.id = links.link_type_id WHERE hreflink = ?''',
                (user_adress,)).fetchone()
            print(href[1])
            flask.flash(f'{user_adress}')

    return render_template('index.html', menu=menu, ms=ms, publicln=publicln, typeln=typeln, baselink=baselink)


@app.route("/href/<hashref>")
def direct(hashref):
    connect = sqlite3.connect('db.db')
    cursor = connect.cursor()
    href = cursor.execute('''SELECT * FROM links INNER JOIN links_types ON links_types.id = links.link_type_id WHERE hreflink = ?''', (hashref, ) ).fetchone()
    print(href)
    if href[5]==1:
        print(href[1])
        return redirect(f"{href[1]}")
    return render_template('index.html', menu=menu)



@app.route("/log", methods=["POST", "GET"])
def log():
    print(session.get('userLogged'))
    if session.get('userLogged') != None:
        return redirect(url_for('index', username=session['userLogged']))
    if request.method == 'POST':
        conn = sqlite3.connect('db.db')
        cur = conn.cursor()
        user = cur.execute('SELECT * FROM users WHERE login = ?', (request.form['login'],)).fetchone()
        pas = cur.execute('SELECT password FROM users')
        if request.method == 'POST' and request.form['login'] == user[1]:
            if check_password_hash(user[2], request.form['password']):
                session['userLogged'] = request.form['login']
                return redirect(url_for('index', username=session['userLogged']))

    return render_template('log.html', menu=menu)


@app.route("/reg", methods=["POST", "GET"])
def reg():
    conn = sqlite3.connect('db.db')
    cur = conn.cursor()

    if request.method == 'POST':
        user = cur.execute('SELECT login FROM users WHERE login = ?', (request.form["login"],)).fetchone()
        if user != None:
            return redirect('/reg', code=302)
        else:
            if request.form['password'] == request.form['password_confirmation']:
                name = request.form['login']
                ps = request.form['password_confirmation']
                hash = generate_password_hash(ps)
                cur.execute("""INSERT INTO users('login', 'password') VALUES(?,?)""", (name, hash))
                conn.commit()
                session['userLogged'] = request.form['login']
                return redirect('/log', code=302)
    return render_template('reg.html', menu=menu)


@app.route("/logout", methods=["POST", "GET"])
def logout():
    session.pop('userLogged', None)
    return redirect(url_for('index'))


@app.route("/delet", methods=["POST", "GET"])
def delete():
    menu = [{'name': 'Выйти', 'url': '/logout'},
            {'name': session.get('userLogged'), 'url': '/log'}]
    conn = sqlite3.connect('db.db')
    cur = conn.cursor()
    cur.execute('''DELETE FROM 'links' WHERE id = ?''', (request.form['idd'],))
    conn.commit()
    user_id = cur.execute('SELECT "id" FROM users WHERE login = ?', (session.get('userLogged'),)).fetchone()
    id1 = user_id[0]
    ms = cur.execute(
        'SELECT * FROM links INNER JOIN links_types ON links_types.id = links.link_type_id  WHERE user_id = ?',
        (id1,)).fetchall()
    return redirect(url_for('index'))


@app.route("/index", methods=["POST", "GET"])
def ism():
    ms = []

    conn = sqlite3.connect('db.db')
    cur = conn.cursor()
    if session.get('userLogged') != None:
        if request.method == 'POST':
            menu = [{'name': 'Выйти', 'url': '/logout'},
                    {'name': session.get('userLogged'), 'url': '/log'}]
            user_id = cur.execute('SELECT "id" FROM users WHERE login = ?', (session.get('userLogged'),)).fetchone()
            id1 = user_id[0]
            ms = cur.execute(
                'SELECT * FROM links INNER JOIN links_types ON links_types.id = links.link_type_id  WHERE user_id = ?',
                (id1,)).fetchall()
            cur.execute('''UPDATE links SET hreflink = ?, link_type_id = ? WHERE id = ?''', (request.form["hrefs"], request.form["type"], request.form["idln"]))
            conn.commit()
            print(request.form["type"])
            print(request.form["hrefs"])
            print(request.form["idln"])
    return redirect(url_for('index'))


if __name__ == "__main__":
    app.run(debug=True)
