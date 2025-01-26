import re, time
from sqlalchemy.exc import IntegrityError
from flask_login import login_user, logout_user, login_required, current_user
from flask import render_template, redirect, url_for
from models import app, db, login_manager, Transaction, User, sysuser_id
import forms

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def is_valid_email(email):
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return re.match(pattern, email) is not None

def define_route():
    @app.route("/account/register", methods=["GET", "POST"])
    def register():
        form = forms.RegistrationForm()
        if form.validate_on_submit():
            # メールアドレスの検証
            if not is_valid_email(form.email.data):
                form.email.errors.append("無効なメールアドレスです。")
                return render_template("account/register.html", form=form)

            try:
                user = User(name=form.name.data, email=form.email.data)
                user.set_password(form.password.data)
                user.balance = 100  # 初期バランスを設定
                db.session.add(user)
                db.session.flush()

                user = db.session.query(User).get(user.id)

                db.session.add(Transaction(sender_id=sysuser_id, receiver_id=user.id, amount=100))

                db.session.commit()

                # 登録後に自動的にログイン
                login_user(user)

                return redirect(url_for("index"))
            except IntegrityError as e:
                db.session.rollback()
                error_message = str(e)
                if "UNIQUE constraint failed" in error_message:
                    form.email.errors.append("メールアドレスは既に使用されています。")
                    return render_template("account/register.html", form=form)
                elif "NOT NULL constraint failed" in error_message:
                    return "必須フィールドが空です。"
                else:
                    return "不明なエラーが発生しました。"
    
        return render_template("account/register.html", form=form)

    @app.route("/account/detail")
    @login_required
    def detail():
        return render_template("account/detail.html", user=current_user)

    @app.route("/account/update", methods=["GET", "POST"])
    @login_required
    def update():
        form = forms.UpdateForm()
        form.name.data = current_user.name
        form.email.data = current_user.email
        if form.validate_on_submit():
            if current_user.check_password(form.password.data):
                current_user.name = form.name.data
                current_user.email = form.email.data
                if form.new_password.data:
                    current_user.set_password(form.new_password.data)
            else:
                form.password.errors.append("パスワードが無効です。")
        return render_template("account/update.html", form=form)

    @app.route("/account/login", methods=["GET", "POST"])
    def login():
        form = forms.LoginForm()
        if form.validate_on_submit():
            user = User.query.filter_by(email=form.email.data).first()
            if user and user.check_password(form.password.data):
                login_user(user)
                return redirect(url_for("index"))
        
            # ログイン失敗時のエラーメッセージ
            form.email.errors.append("メールアドレスまたはパスワードが無効です。")

        return render_template("account/login.html", form=form)

    @app.route("/account/logout")
    def logout():
        logout_user()
        return redirect(url_for("index"))

