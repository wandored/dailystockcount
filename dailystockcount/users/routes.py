''' user/routes.py is the flask routes for user pages '''
from flask import render_template, url_for, flash, redirect, request, Blueprint
from flask_login import login_user, current_user, logout_user, login_required
from flask_admin.contrib.sqla import ModelView
from RandomWordGenerator import RandomWord
from dailystockcount import db, bcrypt
from dailystockcount.models import User
from dailystockcount.users.forms import (RegistrationFrom,
                                         LoginForm,
                                         UpdateAccountForm,
                                         RequestResetForm,
                                         ResetPasswordForm)
from dailystockcount.users.utils import save_picture, send_reset_email, send_welcome_email

users = Blueprint('users', __name__)
# admin.add_view(ModelView(User, db.session))


@users.route("/register/", methods=['GET', 'POST'])
def register():
    ''' route for register.html '''
    user_list = User.query.all()
    form = RegistrationFrom()
    if form.validate_on_submit():
        rw = RandomWord(max_word_size=10)
        hashed_password = bcrypt.generate_password_hash(
            rw.generate()).decode('utf-8')
        user = User(username=form.username.data,
                    email=form.email.data,
                    password=hashed_password)
        db.session.add(user)
        db.session.commit()
        user = User.query.filter_by(email=form.email.data).first()
        send_welcome_email(user)
        flash('Account has been created and an email has been sent with instructions to reset password!', 'success')
        return redirect(url_for('users.register'))
    return render_template('users/register.html',
                           title='Add New User',
                           form=form, user_list=user_list)


@users.route("/login/", methods=['GET', 'POST'])
def login():
    ''' route for login.html '''
    if current_user.is_authenticated:
        return redirect(url_for('users.account'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('counts.count'))
        else:
            flash('Login Unsuccessful. Please check username and password', 'danger')
    return render_template('users/login.html', title='Login', form=form)


@users.route("/logout/")
def logout():
    ''' route for logout.html '''
    logout_user()
    return redirect(url_for('users.login'))


@users.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    ''' route for account.html '''
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Your account has been updated!', 'success')
        return redirect(url_for('users.account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
        image_file = url_for(
            'static', filename='profile_pics/' + current_user.image_file)
    return render_template('users/account.html', title='Account', image_file=image_file, form=form)


@users.route("/user/<int:user_id>/delete", methods=['GET', 'POST'])
@login_required
def delete_user(user_id):
    ''' Delete a user '''
    form = RegistrationFrom()
    user = User.query.get_or_404(user_id)
    if request.method == 'POST':
        db.session.delete(user)
        db.session.commit()
        flash('User has been deleted', 'success')
        return redirect(url_for('users.register'))
    return render_template('users/delete_user.html', title='Add New User', form=form, user=user)


@users.route("/reset_password", methods=['GET', 'POST'])
def reset_request():
    ''' route for reset_password.html '''
    if current_user.is_authenticated:
        flash('You must be logged out to reset your password', 'info')
        return redirect(url_for('users.account'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash('An email has been sent with instructions to reset your password', 'info')
        return redirect(url_for('users.login'))
    return render_template('users/reset_request.html', title='Reset Password', form=form)


@users.route("/reset_password/<token>", methods=['GET', 'POST'])
def reset_token(token):
    ''' route for reset_password/token '''
    if current_user.is_authenticated:
        return redirect(url_for('users.account'))
    user = User.verify_reset_token(token)
    if user is None:
        flash('That is an invalid or expired token', 'warning')
        return redirect(url_for('users.reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(
            form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        flash('Your password has been updated! You are now able to log in', 'success')
        return redirect(url_for('users.login'))
    return render_template('users/reset_token.html', title='Reset Password', form=form)
