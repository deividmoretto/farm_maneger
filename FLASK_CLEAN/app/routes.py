from flask import Blueprint, render_template, redirect, url_for
from .models import Crop, User
from .forms import AddCropForm
from . import db
from .utils import get_sensor_data  # Importe a função

main = Blueprint('main', __name__)

@main.route('/')
def home():
    crops = Crop.query.all()
    return render_template('index.html', crops=crops)

@main.route('/add_crop', methods=['GET', 'POST'])
def add_crop():
    form = AddCropForm()
    if form.validate_on_submit():
        crop = Crop(name=form.name.data, description=form.description.data)
        db.session.add(crop)
        db.session.commit()
        return redirect(url_for('main.home'))
    return render_template('add_crop.html', form=form)

@main.route('/sensor_data')
def sensor_data():
    temperature, humidity = get_sensor_data()  # Utilize a função get_sensor_data
    return render_template('sensor_data.html', temperature=temperature, humidity=humidity)

def init_app(app):
    app.register_blueprint(main)
