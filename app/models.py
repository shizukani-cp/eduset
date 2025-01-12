import time, hashlib
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import ForeignKey
from flask_login import LoginManager

app = Flask(__name__)
app.config["SECRET_KEY"] = "your_secret_key"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///users.db"
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

class User(UserMixin, db.Model):
    __tablename__ = "user"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    balance = db.Column(db.Integer, default=0)
    transactions_sent = db.relationship("Transaction", foreign_keys="Transaction.sender_id", backref="sender", lazy="select")
    transactions_received = db.relationship("Transaction", foreign_keys="Transaction.receiver_id", backref="receiver", lazy="select")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Transaction(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(ForeignKey("user.id"))
    receiver_id = db.Column(ForeignKey("user.id"))
    amount = db.Column(db.Integer)

with app.app_context():
        db.drop_all()
        db.create_all()

        sysuser = User(name="システム",
                       email="system@example.com", # 必須だが不使用
                       password_hash="aaa",        #      〃
                    )

        db.session.add(sysuser)
        db.session.commit()
        db.session.refresh(sysuser)
        sysuser_id = sysuser.id
