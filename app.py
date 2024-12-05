from flask import Flask, render_template, request, redirect
from bs4 import BeautifulSoup
from flask_sqlalchemy import SQLAlchemy

import bcrypt
import requests



app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
db = SQLAlchemy(app)
app.app_context().push()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(30), nullable=False)
    password = db.Column(db.String(30), nullable=False)
    salt = db.Column(db.String(20), default=bcrypt.gensalt())

    def __repr__(self):
        return '<User %r>' % self.id


@app.route('/', methods=['POST', 'GET'])
def index():
    if request.method == 'POST':
        global title
        title = request.form['title']

        return redirect('/products')
    else:
        return render_template('index.html')

@app.route('/products')
def products():
    try:
        units_title_price= parser(title)
        return render_template('products.html', units_title_price=units_title_price)
    except:
        return render_template('products_no_parse.html')





@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        login = request.form['login']
        pass1 = request.form['password1']

        users = User.query.all()

        for user in users:
            if user.login == login:
                bytes_pass = bytes(pass1, 'utf-8')
                if user.password == bcrypt.hashpw(bytes_pass, user.salt):
                    return 'Авторизация успешно проведена'
                else:
                    return 'Проверьте пароль'
    else:
        return render_template('login.html')

@app.route('/registration', methods=['POST', 'GET'])
def registration():
    if request.method == 'POST':
        login = request.form['login']
        pass1 = request.form['password1']
        pass2 = request.form['password2']

        users = User.query.all()

        if pass1 == pass2:

            for user in users:
                if user.login == login:
                    return 'Данный логин уже занят'


            byte_pass = bytes(pass1, 'utf-8')
            salt = bcrypt.gensalt()
            hash_pass = bcrypt.hashpw(byte_pass, salt)

            user = User(login=login, password=hash_pass, salt=salt)

            try:
                db.session.add(user)
                db.session.commit()
                return redirect('/')
            except:
                return 'При регистрации произошла ошибка'
        else:
            return 'Пароли не совпадают'
    else:
        return render_template('reg.html')

def parser(title):
    r = requests.get(f'https://www.divan.ru/category/{title}')
    soup = BeautifulSoup(r.text, 'html.parser')

    all_units = soup.findAll('div', class_='WdR1o')

    units_title_price = []

    for unit in all_units:
        unit_title = unit.find('span', itemprop='name')
        unit_price = unit.find('span', class_='ui-LD-ZU KIkOH')

        units_title_price.append({
            'title': unit_title.text,
            'price': unit_price.text
        })

    print(units_title_price)


    return units_title_price


if __name__ == '__main__':
    app.run()