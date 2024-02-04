from flask_wtf import FlaskForm
from wtforms import EmailField, PasswordField, StringField,DateField
from wtforms.validators import DataRequired, Email, EqualTo, Length

from src.accounts.models import User


class LoginForm(FlaskForm):
    email = EmailField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])


class RecoveryForm(FlaskForm):
    email = EmailField("Email", validators=[DataRequired(), Email()])
    
class ChangePasswordForm(FlaskForm):
    password = PasswordField("Password", validators=[DataRequired(), Length(min=6, max=25)])
    confirm = PasswordField(
        "Repeat password",
        validators=[
            DataRequired(),
            EqualTo("password", message="Passwords must match."),
        ],
    )
    
    def validate(self):
        initial_validation = super(ChangePasswordForm, self).validate()
        if not initial_validation:
            return False
        if self.password.data != self.confirm.data:
            self.password.errors.append("Passwords must match")
            return False
        return True






class RegisterForm(FlaskForm):
    email = EmailField(
        "Email", validators=[DataRequired(), Email(message=None), Length(min=6, max=40)]
    )
    password = PasswordField(
        "Password", validators=[DataRequired(), Length(min=6, max=25)]
    )
    confirm = PasswordField(
        "Repeat password",
        validators=[
            DataRequired(),
            EqualTo("password", message="Passwords must match."),
        ],
    )
    nickname = StringField("Nickname", validators=[DataRequired(), Length(min=2, max=25, message="Nickname must be between 2 and 25 characters")])
    birth_date = DateField("Birth Date", format="%Y-%m-%d", validators=[DataRequired()])

    def validate(self):
        initial_validation = super(RegisterForm, self).validate()
        if not initial_validation:
            return False
        user = User.query.filter_by(email=self.email.data).first()
        if user:
            self.email.errors.append("Email already registered")
            return False
        if self.password.data != self.confirm.data:
            self.password.errors.append("Passwords must match")
            return False
        return True
