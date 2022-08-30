import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from sqlalchemy.exc import IntegrityError
from werkzeug.security import check_password_hash, generate_password_hash

from blog.db import db
from blog.forms import UserLoginForm, UserRegisterForm
from blog.models import User
from blog.utils import is_safe_url

from flask_login import LoginManager, login_user, login_required, logout_user


login_manager = LoginManager()

bp = Blueprint('auth', __name__, url_prefix='/auth')

@login_manager.user_loader
def load_user(user_id):
    user = User.query.get(user_id)
    return user

@bp.route('/register', methods=('GET', 'POST'))
def register():
    form = UserRegisterForm()
    if form.validate_on_submit():
        username = form.data['username']
        password = form.data['password']
        try:
            data = User(username=username, password=generate_password_hash(password))
            db.session.add(data)
            db.session.commit()
        except IntegrityError:
            error = f"User {username} is already registered."
        else:
            return redirect(url_for("auth.login"))

        flash(error)
    return render_template('auth/register.html', form=form)


@bp.route('/login', methods=('GET', 'POST'))
def login():
    form = UserLoginForm()
    if form.validate_on_submit():
        error = None
        username = form.data['username']
        password = form.data['password']
        user = User.query.filter_by(username=username).first()

        if user is None:
            error = 'Incorrect username.'
        elif not check_password_hash(user.password, password):
            error = 'Incorrect password.'

        if error is None:
            login_user(user)
            next = request.args.get('next')
            if next and is_safe_url(next):
                return redirect(next)
            else:
                return redirect(url_for('index'))

        flash(error)

    return render_template('auth/login.html', form=form)

@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))