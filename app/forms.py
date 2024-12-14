from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, IntegerField, SelectField
from wtforms.validators import DataRequired, Email, EqualTo

class RegistrationForm(FlaskForm):
    name = StringField("名前", validators=[DataRequired()])
    email = StringField("メールアドレス", validators=[DataRequired(), Email()])
    password = PasswordField("パスワード", validators=[DataRequired()])
    confirm_password = PasswordField("パスワードの確認", validators=[DataRequired(), EqualTo("password")])
    submit = SubmitField("登録")

class LoginForm(FlaskForm):
    email = StringField("メールアドレス", validators=[DataRequired(), Email()])
    password = PasswordField("パスワード", validators=[DataRequired()])
    submit = SubmitField("ログイン")

class TransferForm(FlaskForm):
    recipient_name = SelectField("送金先", coerce=str)
    amount = IntegerField("送金額", validators=[DataRequired()])
    submit = SubmitField("送金")

