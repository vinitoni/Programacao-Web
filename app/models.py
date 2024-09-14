from app import db
from datetime import datetime

class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(120), unique=True, nullable=False)
    senha = db.Column(db.String(60), nullable=False)
    nome = db.Column(db.String(100), nullable=False)
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(10), default='ativo')
    atualizado_em = db.Column(db.DateTime, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"Usuario('{self.id}', '{self.login}', '{self.nome}', '{self.status}')"
