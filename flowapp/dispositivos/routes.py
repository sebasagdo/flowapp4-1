from flowapp.dispositivos.forms import (PostForm, DateForm)
from flowapp.models import  Device, UserDevice, Categoria, DeviceConsumption, DeviceConfiguration
from flask import render_template, url_for, flash, redirect, request, abort,Blueprint
from flask_login import current_user,login_required
from flowapp import db
from sqlalchemy import text, and_, func
from datetime import datetime, timedelta

dispositivos = Blueprint('dispositivos', __name__)


@dispositivos.route("/post/new", methods=['GET', 'POST'])
@login_required
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        # Commit al Device - Se esta creando un nuevo
        device = Device(serialID=form.title.data)
        db.session.add(device)
        db.session.commit()
        # Obtencion Categoria Seleccionada
        id_categoria = form.category.data
        categoria = Categoria.query.filter_by(id=id_categoria).first()
        # Obtencion Zona
        zona = form.content.data
        device_user = UserDevice(dispUser=device, dispositivo=current_user,
                                active='S', dispCategoria=categoria, zona=zona)
        db.session.add(device_user)
        db.session.commit()
        #Insercion de la informacion de la configuracion del Dispositivo
        user_device_limit = DeviceConfiguration(limitDefined=form.limiteConsumo.data, startDateConfig=form.dateInicioConsumo.data, endDateConfig=form.dateInicioConsumo.data + timedelta(days=form.periocidad.data), userDeviceConfigParent=device_user)
        db.session.add(user_device_limit)
        db.session.commit()
        flash('Su dispositivo se ha registrado!', 'success')
        return redirect(url_for('principal.home'))
    return render_template('create_post.html', title='Nuevo Dispositivo',
                           form=form, legend='Nuevo Dispositivo')


@dispositivos.route("/post/<int:post_id>", methods=['POST', 'GET'])
def post(post_id):
    form = DateForm()
    # Se obtiene el device que ha seleccionado el usuario
    device = UserDevice.query.get_or_404(post_id)
    list_consumos = None

    if request.method == 'GET':
        list_consumos = DeviceConsumption.query.filter_by(
            idUserDevice=device.id)

    elif form.validate_on_submit():
        list_consumos = db.session.query(DeviceConsumption).filter(and_((func.date(
            DeviceConsumption.date) >= form.dateInicio.data), func.date(DeviceConsumption.date) <= form.dateFin.data))
    else:
        flash('La fecha inicial no puede ser mayor que la final', 'warning')
        list_consumos = DeviceConsumption.query.filter_by(
            idUserDevice=device.id)

    return render_template('post.html', device=device, listConsumos=list_consumos, form=form)


@dispositivos.route("/post/<int:post_id>/update", methods=['GET', 'POST'])
@login_required
def update_post(post_id):
    #Se busca El dispositivo_User
    device = UserDevice.query.get_or_404(post_id)
    # Se busca la configuracion del Dispositivo
    device_config = DeviceConfiguration.query.filter_by(userDeviceConfigParent=device).first()
    if device.dispositivo != current_user:
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        device.zona = form.content.data  # Se actualiza la zona
        device.dispUser.serialID = form.title.data  # Se actualiza el SerialID
        device.idDeviceCategoryFK = form.category.data  # Se actualiza la categoria
        device_config.limitDefined = form.limiteConsumo.data 
        device_config.startDateConfig=form.dateInicioConsumo.data
        device_config.endDateConfig=form.dateInicioConsumo.data + timedelta(days=form.periocidad.data)
        db.session.commit()
        flash('Se ha actualizado la información de tu dispositivo!', 'success')
        return redirect(url_for('dispositivos.post', post_id=device.id))
    
    elif request.method == 'GET':
        form.title.data = device.dispUser.serialID
        form.content.data = device.zona
        form.category.data = device.idDeviceCategoryFK 
        form.limiteConsumo.data =  device_config.limitDefined
    return render_template('create_post.html', title='Actualizar Dispositivo',
                           form=form, legend='Actualizar Dispositivo')


@dispositivos.route("/post/<int:post_id>/delete", methods=['POST'])
@login_required
def delete_post(post_id):
    user_device = UserDevice.query.get_or_404(post_id)
    # Se busca la configuracion del Dispositivo asociado
    device_config = DeviceConfiguration.query.filter_by(userDeviceConfigParent=user_device).first()
    if user_device.dispositivo != current_user:
        abort(403)
    db.session.delete(device_config)
    db.session.delete(user_device)
    db.session.delete(user_device.dispUser)
    db.session.commit()
    flash('Se ha eliminado el dispositivo de tu cuenta!', 'success')
    return redirect(url_for('principal.home'))
