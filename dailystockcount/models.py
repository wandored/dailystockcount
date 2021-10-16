""" sqlalchemy database models """
from datetime import datetime
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app
from flask_login import UserMixin, current_user
from dailystockcount import db, login_manager


@login_manager.user_loader
def load_user(user_id):
    """load user_id for user edits"""
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    """User Model"""

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default="default_user.jpeg")
    password = db.Column(db.String(60), nullable=False)
    admin = db.Column(db.Integer, default=0)

    def get_reset_token(self, expires_sec):
        """get password reset token for user"""
        s = Serializer(current_app.config["SECRET_KEY"], expires_sec)
        return s.dumps({"user_id": self.id}).decode("utf-8")

    @staticmethod
    def verify_reset_token(token):
        s = Serializer(current_app.config["SECRET_KEY"])
        try:
            user_id = s.loads(token)["user_id"]
        except:
            return None
        return User.query.get(user_id)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.image_file}')"


class Items(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    itemname = db.Column(db.String(), nullable=False)
    casepack = db.Column(db.Integer)
    count = db.relationship("Invcount", backref="count_id", lazy=True)
    buy = db.relationship("Invcount", backref="buy_id", lazy=True)
    sell = db.relationship("Invcount", backref="sell_id", lazy=True)

    def __repr__(self):
        return f"Items('{self.id}', '{self.itemname}', '{self.casepack}')"


class Invcount(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    trans_date = db.Column(db.Date, nullable=False, default=datetime.utcnow)
    count_time = db.Column(db.String(), nullable=False)
    itemname = db.Column(db.String(), nullable=False)
    casecount = db.Column(db.Integer, nullable=False)
    eachcount = db.Column(db.Integer, nullable=False)
    count_total = db.Column(db.Integer, nullable=False)
    previous_total = db.Column(db.Integer, nullable=False)
    theory = db.Column(db.Integer, nullable=False)
    daily_variance = db.Column(db.Integer, nullable=False)
    item_id = db.Column(db.Integer, db.ForeignKey("items.id"), nullable=False)

    def __repr__(self):
        return f"Invcount('{self.trans_date}', '{self.count_time}', '{self.itemname}', '{self.casecount}', '{self.eachcount}', '{self.count_total}')"


class Purchases(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    trans_date = db.Column(db.Date, nullable=False, default=datetime.utcnow)
    count_time = db.Column(db.String(), nullable=False)
    itemname = db.Column(db.String(), nullable=False)
    casecount = db.Column(db.Integer, nullable=False)
    eachcount = db.Column(db.Integer, nullable=False)
    purchase_total = db.Column(db.Integer, nullable=False)
    item_id = db.Column(db.Integer, db.ForeignKey("items.id"), nullable=False)

    def __repr__(self):
        return f"Purchases('{self.trans_date}', '{self.itemname}', '{self.count_time}', '{self.casecount}', '{self.purchase_total}')"


class Sales(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    trans_date = db.Column(db.Date, nullable=False, default=datetime.utcnow)
    count_time = db.Column(db.String(), nullable=False)
    itemname = db.Column(db.String(), nullable=False)
    eachcount = db.Column(db.Integer, nullable=False)
    waste = db.Column(db.Integer, nullable=False)
    sales_total = db.Column(db.Integer, nullable=False)
    item_id = db.Column(db.Integer, db.ForeignKey("items.id"), nullable=False)

    def __repr__(self):
        return f"Sales('{self.trans_date}', '{self.itemname}', '{self.eachcount}', '{self.waste}', '{self.sales_total}')"
