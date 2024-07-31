from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired

class AddCropForm(FlaskForm):
    name = StringField('Nome da Cultura', validators=[DataRequired()])
    description = TextAreaField('Descrição', validators=[DataRequired()])
    submit = SubmitField('Adicionar Cultura')
