import sqlite3
import os
from flask import Flask, render_template, request, g, flash, redirect, url_for
from FDataBase import FDataBase
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from UserLogin import UserLogin


DATABASE = '/templates/meetings_data.db'
DEBUG = True
SECRET_KEY = 'Albert123'

app = Flask(__name__)
app.config.from_object(__name__)
app.config.update(dict(DATABASE=os.path.join(app.root_path, 'meetings_data.db')))

login_manager = LoginManager(app)


@login_manager.user_loader
def load_user(username):
    print("load_user")
    return UserLogin().fromDB(username, dbase)


def connect_db():
    conn = sqlite3.connect(app.config['DATABASE'])
    conn.row_factory = sqlite3.Row
    return conn


def get_db():
    if not hasattr(g, 'link_db'):
        g.link_db = connect_db()
    return g.link_db


dbase = None


@app.before_request
def before_request():
    global dbase
    db = get_db()
    dbase = FDataBase(db)


@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'link_db'):
        g.link_db.close()


@app.route("/")
def index():
    return render_template('index.html', menu=dbase.getMenu())


@app.route("/login", methods=["POST", "GET"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('profile'))

    if request.method == "POST":
        user = dbase.getUser(request.form['username_'])
        if user and user['password'] == request.form['password']:
            userlogin = UserLogin().create(user)
            rm = True if request.form.get('remainme') else False
            login_user(userlogin, remember=rm)
            return redirect(request.args.get("next") or url_for("profile"))

        flash("Неверная пара логин/пароль", "error")

    return render_template("login.html", menu=dbase.getMenu(), title="Авторизация")


@app.route("/register", methods=["POST", "GET"])
def register():
    if request.method == "POST":
        if len(request.form['name_']) > 4 and len(request.form['username_']) > 4 \
                and len(request.form['password_']) > 4 and request.form['password_'] == request.form['password2_']:
            hash = request.form['password_']
            res = dbase.addUser(request.form['name_'], request.form['username_'], hash)
            if res:
                flash("Вы успешно зарегистрированы", "success")
                return redirect(url_for('login'))
            else:
                flash("Ошибка при добавлении в БД", "error")
        else:
            flash("Неверно заполнены поля", "error")

    return render_template("register.html", menu=dbase.getMenu(), title="Регистрация")


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Вы вышли из аккаунта", "success")
    return redirect(url_for('login'))


@app.route('/profile')
@login_required
def profile():
    return f"""<p><a href="{url_for('logout')}">Выйти из профиля</a>
                <p>user info: {current_user.get_id()}"""


if __name__ == "__site__":
    app.run(debug=True)
