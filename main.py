from flask import Flask, request, jsonify, render_template, redirect, url_for, flash
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your_secret_key'

DATABASE = 'database.db'


def get_db():
    db = sqlite3.connect(DATABASE)
    db.row_factory = sqlite3.Row
    return db


def init_db():
    with app.app_context():
        db = get_db()
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()


@app.route('/initdb')
def initialize_database():
    init_db()
    return 'Banco de dados inicializado'


@app.route('/usuarios', methods=['POST'])
def create_user():
    data = request.json
    login = data.get('login')
    senha = generate_password_hash(data.get('senha'))
    nome = data.get('nome')

    if '@' not in login:
        return jsonify({'message': 'O login deve ser um e-mail válido'}), 400

    db = get_db()
    try:
        db.execute(
            'INSERT INTO usuarios (login, senha, nome, data_criacao, status) VALUES (?, ?, ?, ?, ?)',
            (login, senha, nome, datetime.now(), 'ativo')
        )
        db.commit()
        return jsonify({'message': 'Usuário criado com sucesso!'}), 201
    except sqlite3.IntegrityError:
        return jsonify({'message': 'Usuário com este login já existe!'}), 400
    finally:
        db.close()

@app.route('/usuarios', methods=['GET'])
def get_users():
    db = get_db()
    users = db.execute('SELECT * FROM usuarios').fetchall()
    return render_template('usuarios.html', users=users)

@app.route('/usuarios/<int:id>', methods=['PUT'])
def update_user(id):
    data = request.json
    nome = data.get('nome')
    status = data.get('status')

    db = get_db()
    db.execute(
        'UPDATE usuarios SET nome = ?, status = ?, data_ultima_atualizacao = ? WHERE id = ?',
        (nome, status, datetime.now(), id)
    )
    db.commit()
    return jsonify({'message': 'Usuário atualizado com sucesso!'}), 200

@app.route('/usuarios/<int:id>/bloquear', methods=['POST'])
def block_user(id):
    db = get_db()
    try:
        db.execute('UPDATE usuarios SET status = ? WHERE id = ?', ('bloqueado', id))
        db.commit()
    finally:
        db.close()
    
    return redirect(url_for('get_users'))

@app.route('/usuarios/<int:id>/ativar', methods=['POST'])
def activate_user(id):
    db = get_db()
    try:
        db.execute('UPDATE usuarios SET status = ? WHERE id = ?', ('ativo', id))
        db.commit()
        
        flash(f'Usuário {id} ativado com sucesso!')
    except Exception as e:
        flash('Erro ao ativar o usuário. Tente novamente.')
    finally:
        db.close()
    
    return redirect(url_for('get_users'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        login = request.form['login']
        senha = request.form['senha']

        db = get_db()
        user = db.execute('SELECT * FROM usuarios WHERE login = ?', (login,)).fetchone()

        if user and check_password_hash(user['senha'], senha):
            if user['status'] == 'bloqueado':
                flash('Seu usuário está bloqueado!')
                return redirect(url_for('login'))

            db.execute(
                'UPDATE usuarios SET data_ultima_atualizacao = ? WHERE id = ?',
                (datetime.now(), user['id'])
            )
            db.commit()

            flash('Login bem-sucedido!')
            return redirect(url_for('home'))  # Redirecionar para a rota home
        else:
            flash('Login ou senha incorretos!')
            return redirect(url_for('login'))

    return render_template('login.html')

@app.route('/home')
def home():
    return render_template('home.html')  # Renderiza a tela home.html após o login

@app.route('/')
def login1():
    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        login = request.form['login']
        senha = request.form['senha']
        nome = request.form['nome']

        if '@' not in login:
            flash('O login deve ser um e-mail válido')
            return redirect(url_for('register'))

        senha_encriptada = generate_password_hash(senha)

        db = get_db()
        try:
            db.execute(
                'INSERT INTO usuarios (login, senha, nome, data_criacao, status) VALUES (?, ?, ?, ?, ?)',
                (login, senha_encriptada, nome, datetime.now(), 'ativo')
            )
            db.commit()
            flash('Usuário registrado com sucesso!')
            return redirect(url_for('home'))
        except sqlite3.IntegrityError:
            flash('Este e-mail já está registrado!')
            return redirect(url_for('register'))
        finally:
            db.close()
    return render_template('register.html')

@app.route('/usuarios/<int:id>/editar', methods=['GET'])
def edit_user_form(id):
    db = get_db()
    user = db.execute('SELECT * FROM usuarios WHERE id = ?', (id,)).fetchone()

    if not user:
        flash('Usuário não encontrado!')
        return redirect(url_for('get_users'))

    return render_template('editar_usuario.html', user=user)

@app.route('/usuarios/<int:id>/editar', methods=['POST'])
def edit_user(id):
    nome = request.form.get('nome')
    status = request.form.get('status')  # Usando get para evitar KeyError

    if not nome or not status:
        flash('Nome e status são obrigatórios!')
        return redirect(url_for('edit_user_form', id=id))

    db = get_db()
    db.execute(
        'UPDATE usuarios SET nome = ?, status = ?, data_ultima_atualizacao = ? WHERE id = ?',
        (nome, status, datetime.now(), id)
    )
    db.commit()

    flash('Usuário atualizado com sucesso!')
    return redirect(url_for('get_users'))




if __name__ == '__main__':
    app.run(debug=True)
