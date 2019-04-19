import sys
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from flask_login import current_user
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField, SelectField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from flowapp.models import User, UserProfile, Categoria


class RegistrationForm(FlaskForm):
    username = StringField('Usuario',
                           validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Contraseña', validators=[DataRequired()])
    confirm_password = PasswordField('Confirmar Contraseña',
                                     validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Registarse')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Ese usuario ya existe!. Cambie de usuario')

    def validate_email(self, email):
        profileUser = UserProfile.query.filter_by(email=email.data).first()
        #user = User.query.filter_by(email=email.data).first()
        if profileUser:
            raise ValidationError(
                'El email ya se ha tomado. Por favor usar uno diferente.')


class LoginForm(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Recordarme')
    submit = SubmitField('Login')


class UpdateAccountForm(FlaskForm):
    username = StringField('Usuario',
                           validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    picture = FileField('Actualizar Foto Perfil', validators=[
                        FileAllowed(['jpg', 'png'])])
    submit = SubmitField('Actualizar')

    def validate_username(self, username):
        if username.data != current_user.username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError(
                    'Ese usuario ya existe!. Cambie de usuario')

    def validate_email(self, email):
        if email.data != current_user.profile.email:
            user = UserProfile.query.filter_by(email=email.data).first()

            if user:
                raise ValidationError(
                    'El email ya se ha tomado. Por favor usar uno diferente.')


class PostForm(FlaskForm):
    title = StringField('Serial Dispositivo', validators=[DataRequired()])
    content = TextAreaField('Zona', validators=[DataRequired()])

    category = SelectField('Categoria', coerce=int, choices=[(
        cate.id, cate.title) for cate in Categoria.query.all()])

    submit = SubmitField('Enviar')


class RequestResetForm(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    submit = SubmitField('Solicitar resetear contraseña')

    def validate_email(self, email):

        #
        userProfile = UserProfile.query.filter_by(email=email.data).first()
        if userProfile is None:
            raise ValidationError(
                'No hay ninguna cuenta asociada con ese email!.')


class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirma contraseña',
                                     validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Resetear Contraseña')
