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
from wtforms.fields.html5 import IntegerRangeField
from wtforms.validators import NumberRange

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
    sliderR = IntegerRangeField('Интенсивность красного', [NumberRange(min=1, max=100)])
    sliderG = IntegerRangeField('Интенсивность зеленого', [NumberRange(min=1, max=100)])
    sliderB = IntegerRangeField('Интенсивность голубого', [NumberRange(min=1, max=100)])
    submit = SubmitField('Применить')    
    
    
SECRET_KEY = 'secret'
app.config['UPLOAD_FOLDER'] = IMAGE_FOLDER
app.config['SECRET_KEY'] = SECRET_KEY

bootstrap = Bootstrap(app)
    
def intensity(imagePath, data):
    img = Image.open(imagePath)

    fig = plt.figure()
    ax = fig.add_subplot(1, 2, 1)
    imgplot = plt.imshow(img)

    ax.set_title('Before')

    pixs = img.load()
    for i in range(img.size[0]):
        for j in range(img.size[1]):
            pixs[i,j] = (pixs[i,j][0]*data[0],pixs[i,j][1]*data[1],pixs[i,j][2]*data[2])

    ax = fig.add_subplot(1, 2, 2)
    imgplot = plt.imshow(img)
    ax.set_title('After')

    plt.savefig("./static/images/myFig.png")

@app.route("/", methods=['GET', 'POST'])
def main():
    form = MyForm()
    imagePath = None
    graphPath = None
    if form.validate_on_submit():
        pType = form.upload.data.filename.split('.')[-1]
        imagePath = os.path.join('./static/images', f'photo.{pType}')
        graphPath = os.path.join('./static/images', f'myFig.png')
        # Сохраняем наше загруженное изображение
        form.upload.data.save(imagePath)

        intens = [int(form.sliderR.data/25), int(form.sliderG.data/25), int(form.sliderB.data/25)]
        intensity(imagePath, intens)
        
    return render_template('main.html', form=form, image=imagePath, graph=graphPath)
# Запускаем наше приложение
if __name__ == "__main__":
    app.run(host='127.0.0.1', port=5000)
