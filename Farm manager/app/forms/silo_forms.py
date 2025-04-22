from flask_wtf import FlaskForm
from wtforms import StringField, FloatField, TextAreaField, SelectField, SubmitField, DateField, BooleanField, HiddenField
from wtforms.validators import DataRequired, NumberRange, Length, Optional
from datetime import date

class SiloForm(FlaskForm):
    nome = StringField('Nome do Silo', validators=[DataRequired(), Length(min=3, max=100)])
    tipo = SelectField('Tipo de Silo', choices=[
        ('metalico', 'Metálico'),
        ('concreto', 'Concreto'),
        ('bolsa', 'Silo Bolsa'),
        ('graneleiro', 'Graneleiro'),
        ('armazem', 'Armazém'),
        ('outro', 'Outro')
    ], validators=[DataRequired()])
    capacidade = FloatField('Capacidade (toneladas)', validators=[DataRequired(), NumberRange(min=0.1)], default=500.0)
    localizacao = StringField('Localização', validators=[Length(max=200)])
    data_construcao = DateField('Data de Construção/Aquisição', format='%Y-%m-%d', validators=[Optional()])
    observacoes = TextAreaField('Observações', validators=[Length(max=500)])
    submit = SubmitField('Salvar')


class ArmazenamentoForm(FlaskForm):
    silo_id = SelectField('Silo', coerce=int, validators=[DataRequired()])
    cultura = SelectField('Cultura/Grão', choices=[
        ('milho', 'Milho'),
        ('soja', 'Soja'),
        ('trigo', 'Trigo'),
        ('sorgo', 'Sorgo'),
        ('aveia', 'Aveia'),
        ('cevada', 'Cevada'),
        ('feijao', 'Feijão'),
        ('outro', 'Outro')
    ], validators=[DataRequired()])
    safra = StringField('Safra (Ex: 2023/2024)', validators=[Length(max=20)])
    data_entrada = DateField('Data de Entrada', format='%Y-%m-%d', validators=[DataRequired()], default=date.today)
    quantidade = FloatField('Quantidade (toneladas)', validators=[DataRequired(), NumberRange(min=0.1)], default=1.0)
    umidade = FloatField('Umidade (%)', validators=[Optional(), NumberRange(min=0, max=100)], default=14.0)
    impureza = FloatField('Impureza (%)', validators=[Optional(), NumberRange(min=0, max=100)], default=1.0)
    preco_unitario = FloatField('Preço por Tonelada (R$)', validators=[Optional(), NumberRange(min=0)])
    observacoes = TextAreaField('Observações', validators=[Length(max=500)])
    submit = SubmitField('Registrar Armazenamento')


class MovimentacaoForm(FlaskForm):
    armazenamento_id = HiddenField('ID do Armazenamento', validators=[DataRequired()])
    data = DateField('Data da Saída', format='%Y-%m-%d', validators=[DataRequired()], default=date.today)
    quantidade = FloatField('Quantidade (toneladas)', validators=[DataRequired(), NumberRange(min=0.1)], default=1.0)
    tipo = SelectField('Tipo de Movimentação', choices=[
        ('saida', 'Saída para Venda/Consumo'),
        ('ajuste', 'Ajuste de Estoque')
    ], default='saida')
    destino = StringField('Destino', validators=[Length(max=100)])
    preco_unitario = FloatField('Preço por Tonelada (R$)', validators=[Optional(), NumberRange(min=0)])
    observacoes = TextAreaField('Observações', validators=[Length(max=500)])
    submit = SubmitField('Registrar Saída') 