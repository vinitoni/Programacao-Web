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


# Criar novo usuário (CREATE)
@app.route('/usuarios', methods=['POST'])
def create_user():
    data = request.json
    login = data.get('login')
    senha = generate_password_hash(data.get('senha'))  # Encriptação da senha
    nome = data.get('nome')

    # Verificar se o login é um e-mail válido
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


# Obter todos os usuários (READ)
# Obter todos os usuários (READ)
@app.route('/usuarios', methods=['GET'])
def get_users():
    db = get_db()
    users = db.execute('SELECT * FROM usuarios').fetchall()
    return render_template('usuarios.html', users=users)



# Atualizar um usuário (UPDATE)
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


# Bloquear usuário (DELETE equivalente)
@app.route('/usuarios/<int:id>/bloquear', methods=['POST'])
def block_user(id):
    db = get_db()
    user = db.execute('SELECT * FROM usuarios WHERE id = ?', (id,)).fetchone()

    if user:
        db.execute('UPDATE usuarios SET status = ? WHERE id = ?', ('bloqueado', id))
        db.commit()
        return render_template('bloquear_usuario.html', user=user)
    else:
        flash('Usuário não encontrado.')
        return redirect(url_for('get_users'))


# Tela de Login
# Tela de Login
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

            # Atualizar a data_ultima_atualizacao no login bem-sucedido
            db.execute(
                'UPDATE usuarios SET data_ultima_atualizacao = ? WHERE id = ?',
                (datetime.now(), user['id'])
            )
            db.commit()

            flash('Login bem-sucedido!')
            return redirect(url_for('home'))
        else:
            flash('Login ou senha incorretos!')
            return redirect(url_for('login'))
    return render_template('login.html')



@app.route('/')
def home():
    return render_template('home.html')



@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # Receber dados do formulário
        login = request.form['login']
        senha = request.form['senha']
        nome = request.form['nome']

        # Verificar se o login é um e-mail válido
        if '@' not in login:
            flash('O login deve ser um e-mail válido')
            return redirect(url_for('register'))

        # Encriptar a senha usando hash seguro (bcrypt ou werkzeug.security)
        senha_encriptada = generate_password_hash(senha)

        db = get_db()
        try:
            # Inserir o usuário no banco de dados
            db.execute(
                'INSERT INTO usuarios (login, senha, nome, data_criacao, status) VALUES (?, ?, ?, ?, ?)',
                (login, senha_encriptada, nome, datetime.now(), 'ativo')
            )
            db.commit()
            flash('Usuário registrado com sucesso!')
            return redirect(url_for('login'))  # Redirecionar para a tela de login
        except sqlite3.IntegrityError:
            flash('Este e-mail já está registrado!')
            return redirect(url_for('register'))
        finally:
            db.close()
    return render_template('register.html')

if __name__ == '__main__':
    app.run(debug=True)
