from flask import Flask
from flask import render_template
from flask_wtf import FlaskForm, RecaptchaField
from wtforms import StringField, SubmitField, TextField
from wtforms.validators import DataRequired
from flask_wtf.file import FileField, FileAllowed, FileRequired
from flask_bootstrap import Bootstrap
from werkzeug.utils import secure_filename
import os
from flask import request
from flask import Response
import base64
from PIL import Image
from io import BytesIO
import json
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# инициализируем папку с изображением 
IMAGE_FOLDER = os.path.join('static', 'images')
app = Flask(__name__)
# Визуальная составляющая страницы описывается 
# с помощью наследования нашего класса от FlaskForm
# в котором мы инициализируем поле для загрузки файла,
# поле капчи, текстовое поле и кнопку подтверждения
class MyForm(FlaskForm):
    upload = FileField('Загрузите изображение', validators = 
      [FileRequired(), FileAllowed(['jpg', 'png', 'jpeg'], 'Только картинки!')])
    submit = SubmitField('Применить')    
    
    
SECRET_KEY = 'secret'
app.config['UPLOAD_FOLDER'] = IMAGE_FOLDER
app.config['SECRET_KEY'] = SECRET_KEY

bootstrap = Bootstrap(app)
    
@app.route("/", methods=['GET', 'POST'])
def main():
    form = MyForm()
    imagePath = None
    if form.validate_on_submit():
        photo = form.upload.data.filename.split('.')[-1]
        imagePath = os.path.join('./static/images', f'photo.{photo}')
        # Сохраняем наше загруженное изображение
        form.upload.data.save(imagePath)
    return render_template('main.html', form=form, image=imagePath)
# Запускаем наше приложение
if __name__ == "__main__":
    app.run(host='127.0.0.1', port=5000)
