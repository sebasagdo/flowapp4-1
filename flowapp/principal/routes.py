
from flask import Blueprint, render_template, url_for, flash, redirect, request, abort
from flask_login import current_user
from flowapp.models import UserDevice, DeviceConsumption
from datetime import datetime, timedelta


principal = Blueprint('principal', __name__)


@principal.route("/")
@principal.route("/home")
def home():
    if current_user.is_authenticated:
        page = request.args.get('page', 1, type=int)
        devices = UserDevice.query.filter_by(idUserFK=current_user.id).order_by(
            UserDevice.linkDate.desc()).paginate(page=page, per_page=5)
        #listConsumos = DeviceConsumption.query.filter_by(
            #idUserDevice=49).order_by(DeviceConsumption.date.desc())
        return render_template('home.html', devices=devices, datetime=datetime)
    return render_template('about.html', title='Acerca de')


@principal.route("/about")
def about():
    return render_template('about.html', title='Acerca de')
