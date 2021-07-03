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
#     recaptcha = RecaptchaField()
    color1 = StringField("Введите 1 из 3 вариантов (r/g/b)")
    color2 = StringField("Введите 1 из 3 вариантов (r/g/b)")
    color3 = StringField("Введите 1 из 3 вариантов (r/g/b)")
    submit = SubmitField('Применить')    
    
    
SECRET_KEY = 'secret'
app.config['UPLOAD_FOLDER'] = IMAGE_FOLDER
app.config['SECRET_KEY'] = SECRET_KEY
app.config['RECAPTCHA_USE_SSL'] = False
app.config['RECAPTCHA_PUBLIC_KEY'] = '6LenXSsbAAAAABPqpQZ3RpkDt42hxynW7j7SZxpm'
app.config['RECAPTCHA_PRIVATE_KEY'] = '6LenXSsbAAAAALFvL7os3RcyzKnYADCcTW37GBPH'
app.config['RECAPTCHA_OPTIONS'] = {'theme': 'white'}
bootstrap = Bootstrap(app)

def problem(path, color1, color2, color3):
    # Открываем изображение по указанному пути
    im = Image.open(path)
    # В charValue запишем символы цветов (первая буква)
    # В intValue запишем номер цвета 
    charValue = [color1, color2, color3]
    intValue = [0,0,0]

    # Сохраняем размерность картинки
    x,y = im.size
    # Сохраняем картинку в виде массива numpy
    arr = np.asarray(im)
    # С помощью цикла запишем сумму каждого цвета
    # в заданном порядке
    eachColorSum = [0,0,0]
    for i in range(3):
        charValue[i].lower()
        if "r" in charValue[i]:
            intValue[i] = 0
            eachColorSum[0] = np.sum(arr[:,:,i])
        elif "g" in charValue[i]:
            intValue[i] = 1
            eachColorSum[1] = np.sum(arr[:,:,i])
        else:
            intValue[i] = 2
            eachColorSum[2] = np.sum(arr[:,:,i])

    summ = eachColorSum[0] + eachColorSum[1] + eachColorSum[2]
    # В данном массиве запишем соотношение цвета в процентах
    colorPercent = [0,0,0]
    for i in range (3):
        # Прописываем условие, чтобы избежать ошибки деления на 0
        if summ != 0:
            colorPercent[i] = eachColorSum[i] / summ * 100

    fig, ax = plt.subplots()
    # Используем гистограмму
    # Передаем название для каждой (цвет)
    # и его соответствующее значение
    colorList = ["red", "green", "blue"]
    ax.bar(colorList, colorPercent)
    plt.savefig("./static/images/myFig1.png")
    plt.close()

    # Инициализируем массивы средних 
    # значений по вертикали и горизонтали
    averByHoriz = [[0 for i in range(x)] for j in range(3)]
    averByVert  = [[0 for i in range(y)] for j in range(3)]

    fig, ax = plt.subplots()
    # Записываем средние значения
    # по горизонтали
    for i in range (3):
        for j in range(0, x):
            averByHoriz[i][j] = round(np.sum(arr[:,j,i].mean()))
    
    lin = np.linspace(0, 10, x)
    # Добавляем необходимые значения в график
    for i in range (3):
        ax.plot(lin, averByHoriz[i], color=charValue[i])
    plt.savefig("./static/images/horizontal.png")
    plt.close()


    fig, ax = plt.subplots()
    # Записываем средние значения
    # по вертикали
    for i in range (3):
        for j in range(0, y):
            averByVert[i][j] = round(np.sum(arr[j,:,i].mean()))
        
    lin = np.linspace(0, 10, y)
    # Добавляем необходимые значения в график
    for i in range (3):
        ax.plot(lin, averByVert[i], color=charValue[i])
    plt.savefig("./static/images/vertical.png")
    plt.close()

    
    pixelMap = im.load()

    # Получаем новое изображение на основе "im"
    img = Image.new(im.mode, im.size)
    pixelsNew = img.load()
    # Заменяем цветовые карты в зависимости от введенного порядка
    for i in range(img.size[0]):
        for j in range(img.size[1]):
            # На каждом цикле получаем цвета пикселя
            myList = list(pixelMap[i,j])
            # И наконец, применяем цвет по порядку
            pixelsNew[i,j] = (myList[intValue[0]], 
                 myList[intValue[1]], myList[intValue[2]])
    img.save(path)
    
@app.route("/", methods=['GET', 'POST'])
def main():
    form = MyForm()
    imagePath = None
    graphPath1 = None
    graphPath2 = None
    graphPath3 = None
    if form.validate_on_submit():
        photo = form.upload.data.filename.split('.')[-1]
        imagePath = os.path.join('./static/images', f'photo.{photo}')
        graphPath1 = os.path.join('./static/images', f'myFig1.png')
        graphPath2 = os.path.join('./static/images', f'horizontal.png')
        graphPath3 = os.path.join('./static/images', f'vertical.png')
        # Сохраняем наше загруженное изображение
        form.upload.data.save(imagePath)
        problem(imagePath, form.color1.data, form.color2.data, form.color3.data)
    return render_template('main.html', form=form, image=imagePath, graph1=graphPath1, graph2=graphPath2, graph3=graphPath3)
# Запускаем наше приложение
if __name__ == "__main__":
    app.run(host='127.0.0.1', port=5000)
