from flask import Flask, render_template, redirect, url_for, request
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, IntegerField, SelectField
from wtforms.validators import DataRequired, Email, EqualTo
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.exc import IntegrityError
import hashlib
import time
import re

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    balance = db.Column(db.Integer, default=0)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Block:
    def __init__(self, index, previous_hash, timestamp, data, hash):
        self.index = index
        self.previous_hash = previous_hash
        self.timestamp = timestamp
        self.data = data
        self.hash = hash

class Blockchain:
    def __init__(self):
        self.chain = [self.create_genesis_block()]

    def create_genesis_block(self):
        return Block(0, "0", int(time.time()), "Genesis Block", self.calculate_hash(0, "0", int(time.time()), "Genesis Block"))

    def calculate_hash(self, index, previous_hash, timestamp, data):
        value = str(index) + str(previous_hash) + str(timestamp) + str(data)
        return hashlib.sha256(value.encode('utf-8')).hexdigest()

    def get_latest_block(self):
        return self.chain[-1]

    def add_block(self, new_block):
        new_block.previous_hash = self.get_latest_block().hash
        new_block.hash = self.calculate_hash(new_block.index, new_block.previous_hash, new_block.timestamp, new_block.data)
        self.chain.append(new_block)

blockchain = Blockchain()

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class RegistrationForm(FlaskForm):
    name = StringField('名前', validators=[DataRequired()])
    email = StringField('メールアドレス', validators=[DataRequired(), Email()])
    password = PasswordField('パスワード', validators=[DataRequired()])
    confirm_password = PasswordField('パスワードの確認', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('登録')

class LoginForm(FlaskForm):
    email = StringField('メールアドレス', validators=[DataRequired(), Email()])
    password = PasswordField('パスワード', validators=[DataRequired()])
    submit = SubmitField('ログイン')

class TransferForm(FlaskForm):
    recipient_name = SelectField('送金先', coerce=str)
    amount = IntegerField('送金額', validators=[DataRequired()])
    submit = SubmitField('送金')

def is_valid_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        # メールアドレスの検証
        if not is_valid_email(form.email.data):
            form.email.errors.append("無効なメールアドレスです。")
            return render_template('register.html', form=form)

        try:
            user = User(name=form.name.data, email=form.email.data)
            user.set_password(form.password.data)
            user.balance = 100  # 初期バランスを設定
            db.session.add(user)
            db.session.commit()

            # システムからの初期お金をブロックチェーンに記録
            new_block = Block(len(blockchain.chain), blockchain.get_latest_block().hash,
                              int(time.time()), f"システムから {user.name} へ 100 Z", "")
            blockchain.add_block(new_block)

            # 登録後に自動的にログイン
            login_user(user)

            return redirect(url_for('index'))
        except IntegrityError as e:
            db.session.rollback()
            error_message = str(e)
            if 'UNIQUE constraint failed' in error_message:
                form.email.errors.append("メールアドレスは既に使用されています。")
                return render_template('register.html', form=form)
            elif 'NOT NULL constraint failed' in error_message:
                return "必須フィールドが空です。"
            else:
                return "不明なエラーが発生しました。"
    
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            return redirect(url_for('index'))
        
        # ログイン失敗時のエラーメッセージ
        form.email.errors.append("メールアドレスまたはパスワードが無効です。")

    return render_template('login.html', form=form)

@app.route('/transfer', methods=['GET', 'POST'])
@login_required
def transfer():
    users = User.query.all()
    user_names = [(user.name, user.name) for user in users if user.id != current_user.id]
    
    form = TransferForm()
    
    # プルダウンメニューにユーザー名を設定
    form.recipient_name.choices = user_names
    
    if form.validate_on_submit():
        recipient = User.query.filter_by(name=form.recipient_name.data).first()
        
        if recipient:
            if current_user.balance >= form.amount.data:
                current_user.balance -= form.amount.data
                recipient.balance += form.amount.data
                
                db.session.commit()
                
                new_block = Block(len(blockchain.chain), blockchain.get_latest_block().hash,
                                  int(time.time()), f"送金: {current_user.name} -> {recipient.name} {form.amount.data} Z", "")
                
                blockchain.add_block(new_block)
                
                return redirect(url_for('index'))
            
            else:
                return "送金に失敗しました。残高が不足しています。"
        
        else:
            return "受信者が見つかりませんでした。"
    
    return render_template('transfer.html', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/blockchain')
def blockchain_view():
    return render_template('blockchain.html', blockchain=blockchain)

if __name__ == '__main__':
    with app.app_context():
        db.drop_all()
        db.create_all()
    
    app.run(debug=True)
