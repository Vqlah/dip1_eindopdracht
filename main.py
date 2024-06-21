from flask import Flask, render_template, redirect, url_for, request, flash

from flask_login import login_required, LoginManager, UserMixin, login_user, logout_user, current_user

import sqlite3

from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

app.secret_key = 'supersecretkey'

login_manager = LoginManager()

login_manager.init_app(app)

login_manager.login_view = 'login'

class User(UserMixin):

    pass

@login_manager.user_loader

def user_loader(username):

    conn = sqlite3.connect("./database.db")
    c = conn.cursor()
    c.execute("SELECT * FROM login WHERE username = ?", (username,))

    user_data = c.fetchone()

    conn.close()

    if user_data:
        user = User()
        user.id = user_data[1]

        return user

    return None

@login_manager.request_loader

def request_loader(request):

    username = request.form.get('username')
    conn = sqlite3.connect("./database.db")
    c = conn.cursor()
    c.execute("SELECT * FROM login WHERE username = ?", (username,))
    user_data = c.fetchone()

    conn.close()

    if user_data:

        user = User()
        user.id = user_data[1]

        if check_password_hash(user_data[2], request.form.get('password')):

            return user

    return None

@app.route('/')

def home():

    return render_template('home.html')

@app.route('/login', methods=['GET', 'POST'])

def login():

    if request.method == 'POST':

        username = request.form['username']
        password = request.form['password']
        conn = sqlite3.connect("./database.db")
        c = conn.cursor()
        c.execute("SELECT * FROM login WHERE username = ?", (username,))

        user_data = c.fetchone()

        conn.close()

        if user_data and check_password_hash(user_data[2], password):

            user = User()
            user.id = username
            login_user(user)

            return redirect(url_for('dashboard'))

        flash('Invalid username or password')

    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])

def register():

    if request.method == 'POST':

        username = request.form['username']
        password = request.form['password']
        hashed_password = generate_password_hash(password)
        conn = sqlite3.connect("./database.db")
        c = conn.cursor()
        c.execute("INSERT INTO login (username, password) VALUES (?, ?)", (username, hashed_password))
        conn.commit()
        conn.close()

        flash('Registration successful! Please log in.')

        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/dashboard')

@login_required

def dashboard():
    return render_template('dashboard.html')

from flask import render_template
@app.route('/films')
@login_required
def films():

    return render_template('films.html')

from flask import render_template

@app.route('/telefoonboek')
@login_required
def telefoonboek():
    conn = sqlite3.connect("./database.db")
    c = conn.cursor()
    c.execute("SELECT naam, telefoonnummer FROM telefoonboek")
    telefoonboek = c.fetchall()
    conn.close()
    return render_template('telefoonboek.html', telefoonboek=telefoonboek)

@app.route('/add_contact', methods=['POST'])
@login_required
def add_contact():
    if request.method == 'POST':
        naam = request.form['naam']
        telefoonnummer = request.form['telefoonnummer']
        
        conn = sqlite3.connect("./database.db")
        c = conn.cursor()
        c.execute("INSERT INTO telefoonboek (naam, telefoonnummer) VALUES (?, ?)", (naam, telefoonnummer))
        conn.commit()
        conn.close()
        
        flash('Contact toegevoegd aan het telefoonboek!')
        return redirect(url_for('telefoonboek'))

    conn = sqlite3.connect("./database.db")
    c = conn.cursor()
    c.execute("SELECT telefoonnummer FROM telefoonboek WHERE naam=?", (naam,))
    telefoonnummer = c.fetchone()[0]
    conn.close()
    return render_template('add_contact.html', naam=naam, telefoonnummer=telefoonnummer)

@app.route('/delete_contact/<naam>')
@login_required
def delete_contact(naam):
    conn = sqlite3.connect("./database.db")
    c = conn.cursor()
    c.execute("DELETE FROM telefoonboek WHERE naam=?", (naam,))
    conn.commit()
    conn.close()
    
    flash('Contact verwijderd!')
    return redirect(url_for('telefoonboek'))

@app.route('/edit_contact/<naam>', methods=['GET', 'POST'])
@login_required
def edit_contact(naam):
    if request.method == 'POST':
        nieuwe_naam = request.form.get('nieuwe_naam')
        nieuw_telefoonnummer = request.form.get('nieuw_telefoonnummer')
        
        if not nieuwe_naam or not nieuw_telefoonnummer:
            flash('Vul zowel de nieuwe naam als het nieuwe telefoonnummer in.')
            return redirect(url_for('edit_contact', naam=naam))
        
        with sqlite3.connect("./database.db") as conn:
            c = conn.cursor()
            c.execute("UPDATE telefoonboek SET naam=?, telefoonnummer=? WHERE naam=?", (nieuwe_naam, nieuw_telefoonnummer, naam))
            conn.commit()
        
        flash('Contact bijgewerkt!')
        return redirect(url_for('telefoonboek'))

    with sqlite3.connect("./database.db") as conn:
        c = conn.cursor()
        c.execute("SELECT telefoonnummer FROM telefoonboek WHERE naam=?", (naam,))
        telefoonnummer = c.fetchone()[0]
    
    return render_template('edit_contact.html', naam=naam, telefoonnummer=telefoonnummer)

@app.route('/logout')

@login_required

def logout():
    logout_user()
    return redirect(url_for('home'))

@login_manager.unauthorized_handler

def unauthorized_handler():

    return '''Hij doet het niet...
            <p>
            <a href="/">
            <button>Home</button>
            </a></p>'''

def create_db():

    conn = sqlite3.connect("./database.db")
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS login (id INTEGER PRIMARY KEY, username TEXT, password TEXT)''')    
    c.execute('''CREATE TABLE IF NOT EXISTS telefoonboek (id INTEGER PRIMARY KEY,naam TEXT NOT NULL,telefoonnummer TEXT NOT NULL)''')
    conn.commit()
    conn.close()

create_db()

if __name__ == '__main__':

    app.run(debug=True)