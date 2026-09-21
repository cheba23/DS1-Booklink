from datetime import datetime

from db import db
from flask_login import UserMixin


class Empresa(db.Model):
    __tablename__ = 'empresas'

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    cnpj = db.Column(db.String(18), unique=True, nullable=False)

    data_cadastro = db.Column(
        db.DateTime,
        default=datetime.now
    )

    usuarios = db.relationship(
        'Usuario',
        backref='empresa',
        lazy=True
    )

    livros = db.relationship(
        'Livro',
        backref='empresa',
        lazy=True
    )

    generos = db.relationship(
        'Genero',
        backref='empresa',
        lazy=True
    )

    compradores = db.relationship(
        'Comprador',
        backref='empresa',
        lazy=True
    )

    vendas = db.relationship(
        'Venda',
        backref='empresa',
        lazy=True
    )


class Usuario(UserMixin, db.Model):
    __tablename__ = 'usuarios'

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    senha = db.Column(db.String(255), nullable=False)

    tipo = db.Column(
        db.String(20),
        nullable=False,
        default='funcionario'
    )

    empresa_id = db.Column(
        db.Integer,
        db.ForeignKey('empresas.id'),
        nullable=True
    )

    data_cadastro = db.Column(
        db.DateTime,
        default=datetime.now
    )
    
    vendas = db.relationship(
        'Venda',
        backref='usuario',
        lazy=True
    )


class Genero(db.Model):
    __tablename__ = 'generos'

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(50), nullable=False)

    empresa_id = db.Column(
        db.Integer,
        db.ForeignKey('empresas.id'),
        nullable=False
    )

    data_cadastro = db.Column(
        db.DateTime,
        default=datetime.now
    )


class Livro(db.Model):
    __tablename__ = 'livros'

    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(100), nullable=False)
    autor = db.Column(db.String(100), nullable=False)
    preco = db.Column(db.Float, nullable=False)
    estoque = db.Column(db.Integer, default=0)

    empresa_id = db.Column(
        db.Integer,
        db.ForeignKey('empresas.id'),
        nullable=False
    )

    genero_id = db.Column(
        db.Integer,
        db.ForeignKey('generos.id'),
        nullable=False
    )

    data_cadastro = db.Column(
        db.DateTime,
        default=datetime.now
    )

    genero = db.relationship(
        'Genero',
        backref='livros'
    )
    
class Comprador(db.Model):
    __tablename__ = 'compradores'

    id = db.Column(db.Integer, primary_key=True)

    nome = db.Column(
        db.String(100),
        nullable=False
    )

    email = db.Column(
        db.String(100),
        nullable=False
    )

    telefone = db.Column(
        db.String(20),
        nullable=True
    )

    empresa_id = db.Column(
        db.Integer,
        db.ForeignKey('empresas.id'),
        nullable=False
    )

    data_cadastro = db.Column(
        db.DateTime,
        default=datetime.now
    )

    vendas = db.relationship(
        'Venda',
        backref='comprador',
        lazy=True
    )
    
class Venda(db.Model):
    __tablename__ = 'vendas'

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    comprador_id = db.Column(
        db.Integer,
        db.ForeignKey('compradores.id'),
        nullable=True
    )

    empresa_id = db.Column(
        db.Integer,
        db.ForeignKey('empresas.id'),
        nullable=False
    )

    usuario_id = db.Column(
        db.Integer,
        db.ForeignKey('usuarios.id'),
        nullable=False
    )

    data_venda = db.Column(
        db.DateTime,
        default=datetime.now
    )

    total = db.Column(
        db.Float,
        nullable=False,
        default=0
    )

    itens = db.relationship(
        'ItemVenda',
        backref='venda',
        lazy=True,
        cascade='all, delete-orphan'
    )
    
class ItemVenda(db.Model):
    __tablename__ = 'itens_venda'

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    venda_id = db.Column(
        db.Integer,
        db.ForeignKey('vendas.id'),
        nullable=False
    )

    livro_id = db.Column(
        db.Integer,
        db.ForeignKey('livros.id'),
        nullable=False
    )

    quantidade = db.Column(
        db.Integer,
        nullable=False
    )

    preco_unitario = db.Column(
        db.Float,
        nullable=False
    )

    subtotal = db.Column(
        db.Float,
        nullable=False
    )

    livro = db.relationship(
        'Livro',
        backref='itens_venda'
    )