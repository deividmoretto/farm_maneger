from flask_wtf import FlaskForm
from wtforms import StringField, FloatField, TextAreaField, SelectField, SubmitField
from wtforms.validators import DataRequired, NumberRange, Length

class AreaForm(FlaskForm):
    nome = StringField('Nome da Área/Roça', validators=[DataRequired(), Length(min=3, max=100)])
    cultura = SelectField('Cultura Principal', choices=[
        ('milho', 'Milho'),
        ('soja', 'Soja'),
        ('cafe', 'Café'),
        ('frutas', 'Fruticultura'),
        ('hortalicas', 'Hortaliças'),
        ('pastagem', 'Pastagem'),
        ('outros', 'Outros')
    ], default='soja')
    tamanho = FloatField('Tamanho', validators=[DataRequired(), NumberRange(min=0.1)], default=1.0)
    endereco = StringField('Endereço de Localização', validators=[Length(max=200)])
    latitude = StringField('Latitude', validators=[Length(max=30)])
    longitude = StringField('Longitude', validators=[Length(max=30)])
    descricao = TextAreaField('Descrição', validators=[Length(max=500)])
    submit = SubmitField('Salvar') 