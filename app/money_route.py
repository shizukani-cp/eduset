import time
from flask import render_template, redirect, url_for
from flask_login import login_required, current_user
from models import app, db, User, Block, blockchain
import forms

def define_route():
    @app.route("/money/")
    def money_index():
        return render_template("money/index.html")

    @app.route("/money/transfer", methods=["GET", "POST"])
    @login_required
    def transfer():
        users = User.query.all()
        user_names = [(user.name, user.name) for user in users if user.id != current_user.id]
    
        form = forms.TransferForm()
    
        # プルダウンメニューにユーザー名を設定
        form.recipient_name.choices = user_names
    
        if form.validate_on_submit():
            recipient = User.query.filter_by(name=form.recipient_name.data).first()
        
            # 送金額が0または負でないことを確認
            if form.amount.data <= 0:
                flash("送金額は正の数でなければなりません。", "error")
                return render_template("transfer.html", form=form)

            if recipient:
                if current_user.balance >= form.amount.data:
                    current_user.balance -= form.amount.data
                    recipient.balance += form.amount.data
                
                    db.session.commit()
                
                    new_block = Block(len(blockchain.chain), blockchain.get_latest_block().hash,
                                      int(time.time()), f"送金: {current_user.name} -> {recipient.name} {form.amount.data} Z", "")
                
                    blockchain.add_block(new_block)
                
                    return redirect(url_for("index"))
            
                else:
                    flash("送金に失敗しました。残高が不足しています。", "error")
        
            else:
                flash("受信者が見つかりませんでした。", "error")
    
        return render_template("money/transfer.html", form=form)

    @app.route("/money/blockchain")
    def blockchain_view():
        return render_template("money/blockchain.html", blockchain=blockchain)

