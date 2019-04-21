from wtforms import StringField, TextAreaField, SelectField, SubmitField, DateField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from flowapp.models import Categoria
from flask_wtf import FlaskForm
from datetime import date


class PostForm(FlaskForm):
    title = StringField('Serial Dispositivo', validators=[DataRequired()])
    content = StringField('Zona', validators=[DataRequired()])

    category = SelectField('Categoria', coerce=int, choices=[(
        cate.id, cate.title) for cate in Categoria.query.all()])
    limiteConsumo = StringField('Limite Consumo', validators=[DataRequired()])
    dateInicioConsumo = DateField('Fecha Inicio', validators=[
                           DataRequired()], format="%m/%d/%Y", default=date.today)
    periocidad = SelectField('Periocidad', coerce=int, choices=[(30, 'Mensual'), (60, 'Bimensual'), (90, 'Trimestral')])
    submit = SubmitField('Enviar')


class DateForm(FlaskForm):
    dateInicio = DateField('Fecha Inicio', validators=[
                           DataRequired()], format="%m/%d/%Y", default=date.today)
    dateFin = DateField('Fecha Fin', validators=[
                        DataRequired()], format="%m/%d/%Y", default=date.today)
    submit = SubmitField('Buscar')
    #Funcion para validar que se ingrese correctmente la fecha inicial y final
    def validate_on_submit(self):
        result = super(DateForm, self).validate()
        if (self.dateInicio.data > self.dateFin.data):
            return False
        else:
            return result
