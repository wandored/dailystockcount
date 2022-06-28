""" User utilities """
import os
import secrets
from PIL import Image
from flask import url_for, current_app, render_template
from flask_mail import Message
from dailystockcount import mail


def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(
        current_app.root_path, "static/profile_pics", picture_fn
    )
    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn


def send_reset_email(user):
    token = user.get_reset_token(expires_sec=1800)
    msg = Message("Password Reset Request", recipients=[user.email])
    url = url_for("users.reset_token", _external=True, token=token)
    msg.html = render_template(
        "users/reset_email.html", url=url, email=user.email, username=user.username
    )
    mail.send(msg)


def send_welcome_email(user):
    token = user.get_reset_token(expires_sec=86400)
    msg = Message("Welcome to DailyStockCount.com", recipients=[user.email])
    url = url_for("users.reset_token", _external=True, token=token)
    msg.html = render_template(
        "users/register_email.html", url=url, email=user.email, username=user.username
    )
    mail.send(msg)
