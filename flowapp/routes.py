import os
import sys
import secrets
from PIL import Image
from flask import render_template, url_for, flash, redirect, request, abort
from flowapp import app, db, bcrypt, mail
from flowapp.forms import (RegistrationForm, LoginForm, UpdateAccountForm,
                           PostForm, RequestResetForm, ResetPasswordForm)
from flowapp.models import User, Post, UserProfile, UserSession, Device, UserDevice, Categoria
from flask_login import login_user, current_user, logout_user, login_required
from flask_mail import Message


@app.route("/")
@app.route("/home")
def home():
    if current_user.is_authenticated:
        page = request.args.get('page', 1, type=int)
        devices = UserDevice.query.filter_by(idUserFK=current_user.id).order_by(
            UserDevice.linkDate.desc()).paginate(page=page, per_page=5)

        return render_template('home.html', devices=devices)

    return render_template('about.html', title='Acerca de')

@app.route("/about")
def about():
    return render_template('about.html', title='Acerca de')


@app.route("/registro", methods=['GET', 'POST'])
def registro():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form=RegistrationForm()
    if form.validate_on_submit():
        hashed_password=bcrypt.generate_password_hash(
            form.password.data).decode('utf-8')
        user=User(username=form.username.data,
                    password=hashed_password)
        db.session.add(user)
        db.session.commit()

        userProfile=UserProfile(
            usuario=user, firstName=user.username, lastName=user.username, email=form.email.data, phone='32145')
        db.session.add(userProfile)
        db.session.commit()

        flash('Tu cuenta se ha creado exitosamente. Inicia sesión ahora!', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Registro', form=form)


@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form=LoginForm()
    if form.validate_on_submit():
        # Primero Buscar el Email
        userProfile=UserProfile.query.filter_by(
            email=form.email.data).first()
        # Buscar el usuario Asociado a dicho Email
        user=User.query.filter_by(id=userProfile.id).first()

        usuarioSesion=UserSession(
            userProfile.id, user.username, userProfile.email)
        print(usuarioSesion.__dict__)

        if userProfile and bcrypt.check_password_hash(user.password, form.password.data):
            # Pasar el usuario de sesion
            login_user(user, remember=form.remember.data)
            next_page=request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Datos de inicio Incorrectos. Verificar Usuario y Password', 'danger')
    return render_template('login.html', title='Login', form=form)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))


def save_picture(form_picture):
    random_hex=secrets.token_hex(8)
    _, f_ext=os.path.splitext(form_picture.filename)
    picture_fn=random_hex + f_ext
    picture_path=os.path.join(
        app.root_path, 'static/profile_pics', picture_fn)

    output_size=(125, 125)
    i=Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn


@app.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    form=UpdateAccountForm()
    # Primero Buscar el Email
    userProfile=UserProfile.query.filter_by(
        id=current_user.id).first()

    if form.validate_on_submit():
        if form.picture.data:
            picture_file=save_picture(form.picture.data)
            current_user.image_file=picture_file
        current_user.username=form.username.data
        current_user.email=form.email.data
        db.session.commit()
        flash('Tu cuenta se ha actualizado exitosamente!', 'success')
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.username.data=current_user.username
        form.email.data=userProfile.email
    image_file=url_for(
        'static', filename='profile_pics/' + userProfile.image_file)
    return render_template('account.html', title='Cuenta',
                           image_file=image_file, form=form)


@app.route("/post/new", methods=['GET', 'POST'])
@login_required
def new_post():
    form=PostForm()
    if form.validate_on_submit():
        # Comit al Device
        print('IdCatergoria', form.category.data)
        device=Device(serialID=form.title.data)
        db.session.add(device)
        db.session.commit()
        # Obtencion Categoria Seleccionada
        idCategoria=form.category.data
        categoria=Categoria.query.filter_by(id=idCategoria).first()
        # Obtencion Zona
        zona=form.content.data

        deviceUser=UserDevice(dispUser=device, dispositivo=current_user,
                                active='S', dispCategoria=categoria, zona=zona)
        db.session.add(deviceUser)
        db.session.commit()

        """ post = Post(title=form.title.data,
                    content=form.content.data, author=current_user) """
        """ db.session.add(post)
        db.session.commit() """
        flash('Su dispositivo se ha registrado!', 'success')
        return redirect(url_for('home'))
    return render_template('create_post.html', title='Nuevo Dispositivo',
                           form=form, legend='Nuevo Dispositivo')


@app.route("/post/<int:post_id>")
def post(post_id):
    post=Post.query.get_or_404(post_id)
    return render_template('post.html', title=post.title, post=post)


@app.route("/post/<int:post_id>/update", methods=['GET', 'POST'])
@login_required
def update_post(post_id):
    post=Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    form=PostForm()
    if form.validate_on_submit():
        post.title=form.title.data
        post.content=form.content.data
        db.session.commit()
        flash('Your post has been updated!', 'success')
        return redirect(url_for('post', post_id=post.id))
    elif request.method == 'GET':
        form.title.data=post.title
        form.content.data=post.content
    return render_template('create_post.html', title='Update Post',
                           form=form, legend='Update Post')


@app.route("/post/<int:post_id>/delete", methods=['POST'])
@login_required
def delete_post(post_id):
    post=Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    db.session.delete(post)
    db.session.commit()
    flash('Your post has been deleted!', 'success')
    return redirect(url_for('home'))


@app.route("/user/<string:username>")
def user_posts(username):
    page=request.args.get('page', 1, type=int)
    user=User.query.filter_by(username=username).first_or_404()
    posts=Post.query.filter_by(author=user)\
        .order_by(Post.date_posted.desc())\
        .paginate(page=page, per_page=5)
    return render_template('user_posts.html', posts=posts, user=user)


def send_reset_email(user):
    token=user.get_reset_token()
    msg=Message('Password Reset Request',
                  sender='noreply@demo.com',
                  recipients=[user.email])
    msg.body=f'''To reset your password, visit the following link:
{url_for('reset_token', token=token, _external=True)}

If you did not make this request then simply ignore this email and no changes will be made.
'''
    mail.send(msg)


@app.route("/reset_password", methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form=RequestResetForm()
    if form.validate_on_submit():
        user=User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash('An email has been sent with instructions to reset your password.', 'info')
        return redirect(url_for('login'))
    return render_template('reset_request.html', title='Reset Password', form=form)


@app.route("/reset_password/<token>", methods=['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    user=User.verify_reset_token(token)
    if user is None:
        flash('That is an invalid or expired token', 'warning')
        return redirect(url_for('reset_request'))
    form=ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password=bcrypt.generate_password_hash(
            form.password.data).decode('utf-8')
        user.password=hashed_password
        db.session.commit()
        flash('Tu contraseña se ha actualizado! Inicia sesión ahora', 'success')
        return redirect(url_for('login'))
    return render_template('reset_token.html', title='Reset Password', form=form)
