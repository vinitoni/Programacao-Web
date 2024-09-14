import os

class Config:
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://usuario:senha@localhost/nome_do_banco'
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'uma_chave_secreta_aqui'
