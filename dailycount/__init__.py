from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail
from flask_admin import Admin
from dailycount.config import Config

mail = Mail()
db = SQLAlchemy()
bcrypt = Bcrypt()
admin = Admin()
login_manager = LoginManager()
login_manager.login_view = 'users.login'
login_manager.login_message_category = 'info'


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)
    from dailycount.models import MyAdminView  # noqa
    admin.init_app(app, index_view=MyAdminView())

    from dailycount.users.routes import users  # noqa
    from dailycount.counts.routes import counts  # noqa
    from dailycount.main.routes import main  # noqa
    app.register_blueprint(users)
    app.register_blueprint(counts)
    app.register_blueprint(main)

    return app
