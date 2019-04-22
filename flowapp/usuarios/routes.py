from flask import Blueprint, render_template, url_for, flash, redirect, request, abort
from flask_login import login_user, current_user, logout_user, login_required
from flowapp.usuarios.forms import (RegistrationForm, User, UserProfile, LoginForm, UpdateAccountForm, RequestResetForm, ResetPasswordForm)
from flowapp import db, bcrypt, mail
from flowapp.models import User, UserDevice
from flowapp.usuarios.utilitarios import send_reset_email, save_picture

usuarios = Blueprint('usuarios', __name__)


@usuarios.route("/registro", methods=['GET', 'POST'])
def registro():
    if current_user.is_authenticated:
        return redirect(url_for('principal.home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(
            form.password.data).decode('utf-8')
        user = User(username=form.username.data,
                    password=hashed_password)
        db.session.add(user)
        db.session.commit()

        user_profile = UserProfile(
            usuario=user, firstName=user.username, lastName=user.username, email=form.email.data, phone='32145')
        db.session.add(user_profile)
        db.session.commit()

        flash('Tu cuenta se ha creado exitosamente. Inicia sesión ahora!', 'success')
        return redirect(url_for('usuarios.login'))
    return render_template('register.html', title='Registro', form=form)


@usuarios.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('principal.home'))
    form = LoginForm()
    if form.validate_on_submit():
        # Primero Buscar el Email
        user_profile = UserProfile.query.filter_by(
            email=form.email.data).first()
        # Buscar el usuario Asociado a dicho Email
        user = User.query.filter_by(id=user_profile.id).first()
        if user_profile and bcrypt.check_password_hash(user.password, form.password.data):
            # Pasar el usuario de sesion
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('principal.home'))
        else:
            flash('Datos de inicio Incorrectos. Verificar Usuario y Password', 'danger')
    return render_template('login.html', title='Login', form=form)


@usuarios.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    # Primero Buscar el Email
    user_profile = UserProfile.query.filter_by(
        id=current_user.id).first()

    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            user_profile.image_file = picture_file
        current_user.username = form.username.data
        user_profile.email = form.email.data
        db.session.commit()
        flash('Tu cuenta se ha actualizado exitosamente!', 'success')
        return redirect(url_for('usuarios.account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = user_profile.email
    image_file = url_for(
        'static', filename='profile_pics/' + user_profile.image_file)
    return render_template('account.html', title='Cuenta',
                           image_file=image_file, form=form)


@usuarios.route("/user/<string:username>")
def user_posts(username):
    page = request.args.get('page', 1, type=int)
    user = User.query.filter_by(username=username).first_or_404()
    devices = UserDevice.query.filter_by(idUserFK=current_user.id).order_by(
        UserDevice.linkDate.desc()).paginate(page=page, per_page=5)
    return render_template('user_posts.html', devices=devices, user=user)


@usuarios.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('principal.home'))


@usuarios.route("/reset_password", methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('principal.home'))
    form = RequestResetForm()
    if form.validate_on_submit():
         # Primero Buscar el Email
        user_profile = UserProfile.query.filter_by(
            email=form.email.data).first()
        # Buscar el usuario Asociado a dicho Email
        user = User.query.filter_by(id=user_profile.id).first()
        send_reset_email(user)
        flash('Se ha enviado a su correo electronico las instrucciones de resetar password.', 'info')
        return redirect(url_for('usuarios.login'))
    return render_template('reset_request.html', title='Reset Password', form=form)


@usuarios.route("/reset_password/<token>", methods=['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('principal.home'))
    user = User.verify_reset_token(token)
    if user is None:
        flash('That is an invalid or expired token', 'warning')
        return redirect(url_for('usuarios.reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(
            form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        flash('Tu contraseña se ha actualizado! Inicia sesión ahora', 'success')
        return redirect(url_for('usuarios.login'))
    return render_template('reset_token.html', title='Reset Password', form=form)
