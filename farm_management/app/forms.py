from flask_wtf import FlaskForm
from wtforms.fields import StringField, EmailField, PasswordField, BooleanField, SubmitField, DateField
from wtforms.validators import Length, DataRequired

class LoginForm(FlaskForm):
    email = EmailField("Email")
    senha = PasswordField("Senha", validators=[
        Length(8, 16, "O campo deve conter entre 8 a 16 caracteres.")
    ])
    remember = BooleanField("Permanecer Conectado")
    submit = SubmitField("Entrar")

class CadastroSafraForm(FlaskForm):
    nome = StringField('Nome da Safra', validators=[DataRequired()])
    data_inicio = DateField('Data de Início', format='%Y-%m-%d', validators=[DataRequired()])
    data_fim = DateField('Data de Fim', format='%Y-%m-%d', validators=[DataRequired()])
