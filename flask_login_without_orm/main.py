from os import getenv
from json import load
from typing import Dict, Optional

from urllib.parse import urlparse, urljoin

from flask import Flask, redirect, url_for, request, \
        render_template, flash, abort

from werkzeug.security import generate_password_hash, \
        check_password_hash

from flask_login import (
    LoginManager,
    UserMixin,
    current_user,
    login_required,
    login_user,
    logout_user,
)

from forms import LoginForm

app = Flask(__name__)
app.config["SECRET_KEY"] = getenv("SECRET_KEY", default="secret_key_example")

login_manager = LoginManager(app)

users: Dict[str, "User"] = {}

class User(UserMixin):
    def __init__(self, id: str, username: str, email: str, password: str):
        self.id = id
        self.username = username
        self.email = email
        self.password = generate_password_hash(password)

    @staticmethod
    def get(user_id: str) -> Optional["User"]:
        return users.get(user_id)

    def __str__(self) -> str:
        return f"<Id: {self.id}, Username: {self.username}, Email: {self.email}>"

    def __repr__(self) -> str:
        return self.__str__()

    def verify_password(self, pwd):
        return check_password_hash(self.password, pwd)


with open("users.json") as file:
    data = load(file)
    for key in data:
        users[key] = User(
            id=key,
            username=data[key]["username"],
            email=data[key]["email"],
            password=data[key]["password"],
        )


@login_manager.user_loader
def load_user(user_id: str) -> Optional[User]:
    return User.get(user_id)


@app.get("/")
def index():
    username = "anonymous"
    if current_user.is_authenticated:  # type: ignore
        username = current_user.username  # type: ignore
    return f"""
        <h1>Hi {username}</h1>
        <h3>Welcome to Flask Login without ORM!</h3>
    """


def is_safe_url(target):
    """
    is_safe_url should check if the url is safe for redirects.
    See http://flask.pocoo.org/snippets/62/ for an example.
    """
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and \
           ref_url.netloc == test_url.netloc

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm(request.form)
    if request.method == 'POST' and form.validate():
        user_id = 0
        for user in users:
            if form.username.data == users[user].username:
                user_id = user

        if int(user_id) > 0 and int(user_id) < len(users):
            user = User.get(user_id)

            # Login and validate the user. (returns User() instance)
            if user.verify_password(form.password.data):
                login_user(user)

                flash('Logged in successfully.')

                next = request.args.get('next')
                if not is_safe_url(next):
                    return abort(400)

                return redirect(next or url_for('index'))
            else:
                flash('Incorrect password.')
        else:
            flash('User not found.')
    return render_template('login.html', form=form)

@app.get("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("index"))


@app.get("/settings")
@login_required
def settings():
    return "<h1>Route protected</h1>"
