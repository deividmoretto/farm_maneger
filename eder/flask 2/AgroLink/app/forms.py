from flask_wtf import FlaskForm
from wtforms import EmailField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length

class LoginForm(FlaskForm):
    email = EmailField("Email", validators=[DataRequired()])
    senha = PasswordField("Senha", validators=[DataRequired(), Length(min=3, max=16)])
    remember = BooleanField("Permanecer Conectado")
    submit = SubmitField("Entrar")