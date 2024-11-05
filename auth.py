from flask import Blueprint, render_template, redirect, url_for, request, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, logout_user
from .models import User
from . import db
from typing import Union

auth = Blueprint('auth', __name__)

@auth.route('/login')
def login() -> str:
    """Render the login page."""
    return render_template('login.html')

@auth.route('/login', methods=['POST'])
def login_post() -> Union[str, redirect]:
    """Handle the login form submission."""
    username = request.form.get('username')
    password = request.form.get('password')
    remember = bool(request.form.get('remember'))

    if not username or not password:
        flash('Please provide both username and password.')
        return redirect(url_for('auth.login'))

    user = User.query.filter_by(username=username).first()

    if not user or not check_password_hash(user.password, password):
        flash('Please check your login details and try again.')
        return redirect(url_for('auth.login'))

    login_user(user, remember=remember)
    return redirect(url_for('main.profile'))

@auth.route('/signup')
def signup() -> str:
    """Render the signup page."""
    return render_template('signup.html')

@auth.route('/signup', methods=['POST'])
def signup_post() -> Union[str, redirect]:
    """Handle the signup form submission."""
    username = request.form.get('username')
    password = request.form.get('password')

    if not username or not password:
        flash('Please provide both username and password.')
        return redirect(url_for('auth.signup'))

    if len(password) < 8:
        flash('Password must be at least 8 characters long.')
        return redirect(url_for('auth.signup'))

    user = User.query.filter_by(username=username).first()

    if user:
        flash('Username already exists.')
        return redirect(url_for('auth.signup'))

    new_user = User(username=username, password=generate_password_hash(password, method='sha256'))

    try:
        db.session.add(new_user)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        flash(f'An error occurred while creating your account: {str(e)}')
        return redirect(url_for('auth.signup'))

    flash('Account created successfully. Please log in.')
    return redirect(url_for('auth.login'))

@auth.route('/logout')
@login_required
def logout() -> redirect:
    """Handle user logout."""
    logout_user()
    return redirect(url_for('main.index'))
