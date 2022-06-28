"""
dailystockcount app initialization
"""

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail
from dailystockcount.config import Config

mail = Mail()
db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()
login_manager.login_view = "main.home"
login_manager.login_message_category = "info"


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)

    from dailystockcount.users.routes import users  # noqa
    from dailystockcount.counts.routes import counts  # noqa
    from dailystockcount.main.routes import main  # noqa
    from dailystockcount.errors.handlers import errors  # noqa

    app.register_blueprint(users)
    app.register_blueprint(counts)
    app.register_blueprint(main)
    app.register_blueprint(errors)

    return app
