import os
import secrets
from PIL import Image
from flask import url_for
from flask_mail import Message
from flowapp import app, mail


def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(
        app.root_path, 'static/profile_pics', picture_fn)

    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn


def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message('Solicitud de cambio de clave FLOWAPP',
                  sender='noreply@demo.com',
                  recipients=[user.profile.email])
    msg.body = f'''Haga Click en el siguiente link para resetar tu password:
{url_for('usuarios.reset_token', token=token, _external=True)}

Si no realizó esta solicitud, simplemente ignore este correo electrónico y no se realizarán cambios.
'''
    mail.send(msg)
