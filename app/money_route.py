from flask import render_template, redirect, url_for, flash
from sqlalchemy import or_
from flask_login import login_required, current_user
from models import app, db, User, Transaction, sysuser_id
import forms

def define_route():
    @app.route("/money/")
    def money_index():
        return render_template("money/index.html")

    @app.route("/money/transfer", methods=["GET", "POST"])
    @login_required
    def transfer():
        users = User.query.filter(~User.id.in_([current_user.id, sysuser_id])).all()
        user_names = [(user.id, user.name) for user in users]

        form = forms.TransferForm()

        # プルダウンメニューにユーザー名を設定
        form.recipient_id.choices = user_names
    
        if form.validate_on_submit():
            recipient = User.query.filter_by(id=form.recipient_id.data).first()

            # 送金額が0または負でないことを確認
            if form.amount.data <= 0:
                flash("送金額は正の数でなければなりません。", "error")
                return render_template("money/transfer.html", form=form)

            if recipient:
                if current_user.balance >= form.amount.data:
                    current_user.balance -= form.amount.data
                    recipient.balance += form.amount.data

                    db.session.add(Transaction(
                                        sender_id=current_user.id,
                                        receiver_id=recipient.id,
                                        amount=form.amount.data))
                    db.session.commit()
                    return redirect(url_for("index"))

                else:
                    flash("送金に失敗しました。残高が不足しています。", "error")

            else:
                flash("受信者が見つかりませんでした。", "error")
    
        return render_template("money/transfer.html", form=form)

    @app.route("/money/transactions")
    @login_required
    def transaction_view():
        return render_template(
                    "money/transactions.html",
                    transactions=db.session.query(
                        Transaction
                    ).filter(
                        or_(Transaction.sender_id == current_user.id, Transaction.receiver_id == current_user.id)
                    ).all())
