from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired

#Formulário para adicionar uma nova cultura à aplicação.
class AddCropForm(FlaskForm):

    # Campo de texto para o nome da cultura, obrigatório
    name = StringField('Nome da Cultura', validators=[DataRequired()])
    
    # Campo de área de texto para a descrição da cultura, obrigatório
    description = TextAreaField('Descrição', validators=[DataRequired()])
    
    # Botão de submissão do formulário
    submit = SubmitField('Adicionar Cultura')
