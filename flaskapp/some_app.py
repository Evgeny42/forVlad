import os
from math import ceil
from flask import Flask
from flask import render_template
from flask_wtf import FlaskForm, RecaptchaField
from wtforms import StringField, SubmitField, TextField
from wtforms.validators import DataRequired
from flask_wtf.file import FileField, FileAllowed, FileRequired
from flask_bootstrap import Bootstrap
from werkzeug.utils import secure_filename
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


app = Flask(__name__)

# Форма состоит из 4 бегунков (3 для отдельного цвета и 1 для всех)
class MyForm(FlaskForm):
    upload = FileField('Загрузите изображение', validators = 
                       [FileRequired(), FileAllowed(['jpg', 'png', 'jpeg'], 'Только картинки!')])
    sliderR = IntegerRangeField('Интенсивность красного', [NumberRange(min=0, max=100)])
    sliderG = IntegerRangeField('Интенсивность зеленого', [NumberRange(min=0, max=100)])
    sliderB = IntegerRangeField('Интенсивность голубого', [NumberRange(min=0, max=100)])
    sliderRGB = IntegerRangeField('Общая интенсивность', [NumberRange(min=0, max=100)])
    submit = SubmitField('Применить')    
    
    
SECRET_KEY = 'secret'
app.config['SECRET_KEY'] = SECRET_KEY
bootstrap = Bootstrap(app)
    
# Функция, которая изменяет интенсивность цветов
def intensity(imagePath, data):
    # Для каждого графика "Открываем" картинку
    img1 = Image.open(imagePath)
    img2 = Image.open(imagePath)
    # Если картинка слишком большая, то уменьшаем ее размер 
    if img1.size[0] > 600 or img1.size[1] > 600:
        img2 = img2.resize([600,int(600*(img1.size[1]/img1.size[0]))])
        img1 = img1.resize([600,int(600*(img1.size[1]/img1.size[0]))])
        
    # ПЕРВЫЙ ГРАФИК    
    fig = plt.figure()
    ax = fig.add_subplot(1, 2, 1)
    imgplot = plt.imshow(img1)
    ax.set_title('Before')
    pixs = img1.load()
    # Проходясь по каждому пикселю
    # Изменяем значение цветовых карт
    for i in range(img1.size[0]):
        for j in range(img1.size[1]):
            pixs[i,j] = (ceil(pixs[i,j][0]*data[0]), 
                         ceil(pixs[i,j][1]*data[1]), 
                         ceil(pixs[i,j][2]*data[2]))
    ax = fig.add_subplot(1, 2, 2)
    imgplot = plt.imshow(img1)
    ax.set_title('After')
    plt.savefig("./static/images/my1Fig.png")
    plt.close()

    # ВТОРОЙ ГРАФИК
    fig = plt.figure()
    ax = fig.add_subplot(1, 2, 1)
    imgplot = plt.imshow(img2)
    ax.set_title('Before')
    pixs = img2.load()
    # Проходясь по каждому пикселю
    # Изменяем значение цветовых карт
    for i in range(img2.size[0]):
        for j in range(img2.size[1]):
            pixs[i,j] = (ceil(pixs[i,j][0]*data[3]), ceil(pixs[i,j][1]*data[3]), ceil(pixs[i,j][2]*data[3]))
    ax = fig.add_subplot(1, 2, 2)
    imgplot = plt.imshow(img2)
    ax.set_title('After')
    plt.savefig("./static/images/my2Fig.png")
    

@app.route("/", methods=['GET', 'POST'])
def main():
    form = MyForm()
    # Объявляем пути к объектам
    imagePath = None
    graph1Path = None
    graph2Path = None
    if form.validate_on_submit():
        # Получаем расширение входного изображения
        pType = form.upload.data.filename.split('.')[-1]
        # Сохраняем путь к картинке
        imagePath = os.path.join('./static/images', f'photo.{pType}')
        # Сохраняем пути к графикам
        graph1Path = os.path.join('./static/images', f'my1Fig.png')
        graph2Path = os.path.join('./static/images', f'my2Fig.png')
        # Сохраняем наше загруженное изображение
        form.upload.data.save(imagePath)
        # Объявляем и преобразуем список со значениями полученными с бегунков
        intens = [form.sliderR.data/25, form.sliderG.data/25, form.sliderB.data/25, form.sliderRGB.data/25]
        # Передаем в функцию путь к картинке и список со значениями
        intensity(imagePath, intens)
    # Передаем в шаблон форму, пути к картинке и графикам
    return render_template('main.html', form=form, image=imagePath, graph1=graph1Path, graph2=graph2Path)
# Запускаем наше приложение
if __name__ == "__main__":
    app.run(host='127.0.0.1', port=5000)
