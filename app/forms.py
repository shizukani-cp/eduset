from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, IntegerField, SelectField
from wtforms.validators import DataRequired, Email, EqualTo
from models import UserRole

class RegistrationForm(FlaskForm):
    name = StringField("名前", validators=[DataRequired()])
    email = StringField("メールアドレス", validators=[DataRequired(), Email()])
    role = SelectField("役割", choices=UserRole.choices(), coerce=int)
    password = PasswordField("パスワード", validators=[DataRequired()])
    confirm_password = PasswordField("パスワードの確認", validators=[DataRequired(), EqualTo("password")])
    submit = SubmitField("登録")

class LoginForm(FlaskForm):
    email = StringField("メールアドレス", validators=[DataRequired(), Email()])
    password = PasswordField("パスワード", validators=[DataRequired()])
    submit = SubmitField("ログイン")

class UpdateForm(FlaskForm):
    name = StringField("名前", validators=[DataRequired()])
    email = StringField("メールアドレス", validators=[DataRequired(), Email()])
    new_password = PasswordField("新しいパスワード", validators=[])
    confirm_new_password = PasswordField("新しいパスワードの確認", validators=[EqualTo("new_password")])
    password = PasswordField("現在のパスワード", validators=[DataRequired()])
    submit = SubmitField("登録")

class TransferForm(FlaskForm):
    recipient_id = SelectField("送金先", coerce=int)
    amount = IntegerField("送金額", validators=[DataRequired()])
    submit = SubmitField("送金")

class CreateClassForm(FlaskForm):
    name = StringField("名前", validators=[DataRequired()])
    submit = SubmitField("作成")
