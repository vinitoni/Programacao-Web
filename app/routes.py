from app import app, db, bcrypt
from app.models import Usuario  # Certifique-se de que isso está correto
from flask import request, render_template, redirect, url_for
import re

@app.route('/initdb', methods=['GET'])
def initdb():
    db.create_all()
    return "Database initialized!"

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        dados = request.form
        login = dados.get('login')
        senha = dados.get('senha')
        nome = dados.get('nome')

        if not re.match(r"[^@]+@[^@]+\.[^@]+", login):
            return "Formato de e-mail inválido.", 400

        if Usuario.query.filter_by(login=login).first():
            return "Já existe um usuário com este e-mail.", 400

        senha_hash = bcrypt.generate_password_hash(senha).decode('utf-8')
        novo_usuario = Usuario(login=login, senha=senha_hash, nome=nome)
        db.session.add(novo_usuario)
        db.session.commit()

        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        login = request.form['login']
        password = request.form['password']
        user = User.query.filter_by(login=login).first()
        if user and bcrypt.check_password_hash(user.password, password):
            if user.status == 'ativo':
                return redirect(url_for('dashboard'))
            else:
                return "User is blocked.", 403
        return "Invalid login or password.", 403
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/manage_users')
def manage_users():
    users = User.query.all()
    return render_template('manage_users.html', users=users)