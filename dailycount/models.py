from datetime import datetime
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app
from flask_login import UserMixin
from dailycount import db, login_manager


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False,
                           default='default_user.jpeg')
    password = db.Column(db.String(60), nullable=False)
    counts = db.relationship('Invcount', backref='manager', lazy=True)

    def get_reset_token(self, expires_sec=1800):
        s = Serializer(current_app.config['SECRET_KEY'], expires_sec)
        return s.dumps({'user_id': self.id}).decode('utf-8')

    @staticmethod
    def verify_reset_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)['user_id']
        except:
            return None
        return User.query.get(user_id)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.image_file}')"


class Invcount(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    trans_date = db.Column(db.DateTime, nullable=False,
                           default=datetime.utcnow)
    count_time = db.Column(db.String(), nullable=False)
    itemname = db.Column(db.String(), nullable=False)
    casecount = db.Column(db.Integer)
    eachcount = db.Column(db.Integer)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f"Invcount('{self.trans_date}', '{self.count_time}', '{self.itemname}', '{self.casecount}', '{self.eachcount}')"


class Purchases(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    trans_date = db.Column(db.DateTime, nullable=False,
                           default=datetime.utcnow)
    itemname = db.Column(db.String(), nullable=False)
    casepack = db.Column(db.Integer)
    casecount = db.Column(db.Integer)

    def __repr__(self):
        return f"Purchases('{self.trans_date}', '{self.itemname}', '{self.casepack}', '{self.casecount}')"


class Sales(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    trans_date = db.Column(db.DateTime, nullable=False,
                           default=datetime.utcnow)
    itemname = db.Column(db.String(), nullable=False)
    eachcount = db.Column(db.Integer)
    waste = db.Column(db.Integer)

    def __repr__(self):
        return f"Sales('{self.trans_date}', '{self.itemname}', '{self.eachcount}', '{self.waste}')"


class Items(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    itemname = db.Column(db.String(), nullable=False)
    casepack = db.Column(db.Integer)

    def __repr__(self):
        return f"Items('{self.id}', '{self.itemname}', '{self.casepack}')"


class CountTotals(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    trans_date = db.Column(db.DateTime, nullable=False,
                           default=datetime.utcnow)
    itemname = db.Column(db.String(), nullable=False)
    onhand = db.Column(db.Integer)
    theory = db.Column(db.Integer)
    variance = db.Column(db.Integer)
