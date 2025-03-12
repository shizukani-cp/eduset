import os
from enum import Enum
from flask import Flask
from flask_login import LoginManager, UserMixin
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import NoResultFound
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config["SECRET_KEY"] = "your_secret_key"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///users.db"
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

class Enum(Enum):
    @classmethod
    def choices(cls):
        return [(choice.value, choice.name) for choice in cls]

class UserRole(Enum):
    student = 10
    teacher = 20
    administrator = 30


# account
class User(UserMixin, db.Model):
    __tablename__ = "user"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    balance = db.Column(db.Integer, default=0)
    role = db.Column(db.Integer, nullable=False)
    transactions_sent = db.relationship("Transaction", foreign_keys="Transaction.sender_id", backref="sender", lazy="select")
    transactions_received = db.relationship("Transaction", foreign_keys="Transaction.receiver_id", backref="receiver", lazy="select")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

# money
class Transaction(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.ForeignKey("user.id"))
    receiver_id = db.Column(db.ForeignKey("user.id"))
    amount = db.Column(db.Integer)

# class
class Class(db.Model):

    __tablename__ = "class"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    parent_id = db.Column(db.Integer, db.ForeignKey("class.id"), nullable=False)

class ClassUser(db.Model):

    __tablename__ = "user_class"

    class_id = db.Column(db.Integer, db.ForeignKey("class.id"), primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), primary_key=True)

with app.app_context():
    drop = os.environ.get("DROP")
    if drop.lower() == "true":
        db.drop_all()
    elif drop.lower() == "false":
        pass
    else:
        raise ValueError("DROPの値が無効です")
    db.create_all()
    try:
        sysuser = db.session.query(User).filter(User.email == "system@example.com").one()
        rootclass = db.session.query(Class).filter(Class.id == Class.parent_id).one()
    except NoResultFound:
        sysuser = User(name="システム",
                       email="system@example.com", # 必須だが不使用
                       password_hash="aaa",        #      〃
                       role=30                     # administrator
                    )
        db.session.add(sysuser)
        rootclass = Class(name="ルート",
                          parent_id=1
                      )
        db.session.add(rootclass)
        db.session.commit()
        rootclass.parent_id = rootclass.id
        db.session.refresh(sysuser)
        db.session.refresh(rootclass)
        db.session.commit()
    sysuser_id = sysuser.id
    rootclass_id = rootclass.id
