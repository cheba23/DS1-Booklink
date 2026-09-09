from flask import Flask, render_template, request, redirect, url_for
from db import db
from models import Genero, Livro, Usuario
from sqlalchemy import or_
# Importa as funções do Flask-Login
from flask_login import (
    LoginManager,      # Gerencia o sistema de login
    login_user,        # Faz o usuário entrar na conta
    login_required,    # Obriga o usuário estar logado para acessar uma rota
    logout_user,       # Faz o usuário sair da conta
    current_user       # Representa o usuário que está logado atualmente
)
# Biblioteca usada para criar o hash da senha
import hashlib

app = Flask(__name__)
lm = LoginManager(app)
lm.login_view = 'login'
app.secret_key = 'eduardo23'
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///dados.db"
db.init_app(app)


def hash(txt):

    # Cria um objeto SHA-256 usando o texto recebido
    hash_obj = hashlib.sha256(txt.encode('utf-8'))

    # Retorna o hash transformado em texto hexadecimal
    return hash_obj.hexdigest()


@lm.user_loader
def user_loader(id):

    # Procura no banco o usuário que possui esse ID
    usuario = db.session.query(Usuario).filter_by(id=id).first()
    return usuario



@app.route('/')
@login_required
def home():
    return render_template('homeAdm.html')

@app.route('/registrar', methods=['GET', 'POST'])
@login_required
def registrar():
    
    if current_user.tipo != 'Admin':
        return redirect(url_for('home'))

    if request.method == 'GET':
        generos = Genero.query.all()
        return render_template('registrar.html', generos=generos)

    elif request.method == 'POST':

        titulo = request.form['tituloForm'].strip()
        autor = request.form['autorForm'].strip()

        if not titulo:
            generos = Genero.query.all()
            return render_template(
                'registrar.html',
                generos=generos,
                erro='O título é obrigatório'
            )

        if not autor:
            generos = Genero.query.all()
            return render_template(
                'registrar.html',
                generos=generos,
                erro='O autor é obrigatório'
            )

        try:
            preco = float(request.form['precoForm'].strip())
        except ValueError:
            generos = Genero.query.all()
            return render_template(
                'registrar.html',
                generos=generos,
                erro='O preço é obrigatório e deve ser um número'
            )

        if preco < 0:
            generos = Genero.query.all()
            return render_template(
                'registrar.html',
                generos=generos,
                erro='O preço não pode ser negativo'
            )

        try:
            estoque = int(request.form['estoqueForm'].strip())
        except ValueError:
            generos = Genero.query.all()
            return render_template(
                'registrar.html',
                generos=generos,
                erro='O estoque é obrigatório e deve ser um número'
            )

        if estoque < 0:
            generos = Genero.query.all()
            return render_template(
                'registrar.html',
                generos=generos,
                erro='O estoque não pode ser negativo'
            )

        try:
            genero_id = int(request.form['genero_id'].strip())
        except ValueError:
            generos = Genero.query.all()
            return render_template(
                'registrar.html',
                generos=generos,
                erro='O gênero é obrigatório'
            )

        novo_livro = Livro(
            titulo=titulo,
            autor=autor,
            preco=preco,
            estoque=estoque,
            genero_id=genero_id
        )

        db.session.add(novo_livro)
        db.session.commit()

        return redirect(url_for('home'))
    
    
@app.route('/livros')
@login_required
def livros():
    busca = request.args.get('busca', '').strip()

    if current_user.tipo != 'Admin':
            return redirect(url_for('home'))
        
    if busca:
        livros = Livro.query.join(Genero).filter(or_(
        Livro.titulo.ilike(f'%{busca}%'),
        Livro.autor.ilike(f'%{busca}%'),
        Genero.nome.ilike(f'%{busca}%')
    )
        ).all()
    else:
        livros = Livro.query.all()

    return render_template(
        'livros.html',
        livros=livros,
        busca=busca
    )

@app.route('/editar/<int:id>', methods=['GET', 'POST'])
@login_required
def editar(id):
    
    if current_user.tipo != 'Admin':
            return redirect(url_for('home'))

    livro = db.session.get(Livro, id)

    if not livro:
        return "Livro não encontrado", 404

    if request.method == 'GET':
        generos = Genero.query.all()

        return render_template(
            'editar.html',
            livro=livro,
            generos=generos
        )

    elif request.method == 'POST':

        titulo = request.form['tituloForm'].strip()
        autor = request.form['autorForm'].strip()

        if not titulo:
            generos = Genero.query.all()

            return render_template(
                'editar.html',
                livro=livro,
                generos=generos,
                erro='O título é obrigatório'
            )

        if not autor:
            generos = Genero.query.all()

            return render_template(
                'editar.html',
                livro=livro,
                generos=generos,
                erro='O autor é obrigatório'
            )

        try:
            preco = float(request.form['precoForm'].strip())
        except ValueError:
            generos = Genero.query.all()

            return render_template(
                'editar.html',
                livro=livro,
                generos=generos,
                erro='O preço é obrigatório e deve ser um número'
            )

        if preco < 0:
            generos = Genero.query.all()

            return render_template(
                'editar.html',
                livro=livro,
                generos=generos,
                erro='O preço não pode ser negativo'
            )

        try:
            estoque = int(request.form['estoqueForm'].strip())
        except ValueError:
            generos = Genero.query.all()

            return render_template(
                'editar.html',
                livro=livro,
                generos=generos,
                erro='O estoque é obrigatório e deve ser um número'
            )

        if estoque < 0:
            generos = Genero.query.all()

            return render_template(
                'editar.html',
                livro=livro,
                generos=generos,
                erro='O estoque não pode ser negativo'
            )

        try:
            genero_id = int(request.form['genero_id'].strip())
        except ValueError:
            generos = Genero.query.all()

            return render_template(
                'editar.html',
                livro=livro,
                generos=generos,
                erro='O gênero é obrigatório'
            )

        # Atualiza o livro
        livro.titulo = titulo
        livro.autor = autor
        livro.preco = preco
        livro.estoque = estoque
        livro.genero_id = genero_id

        db.session.commit()

        return redirect(url_for('livros'))
    
@app.route('/deletar/<int:id>')
@login_required
def deletar(id):
    
    if current_user.tipo != 'Admin':
            return redirect(url_for('home'))
    
    livro = db.session.query(Livro).filter_by(id=id).first()
    
    if not livro:
        return "Livro não encontrado", 404
    
    db.session.delete(livro)
    db.session.commit()
    
    return redirect(url_for('livros'))

@app.route('/generos')
@login_required
def generos():
    
    if current_user.tipo != 'Admin':
            return redirect(url_for('home'))
    
    generos = Genero.query.all()

    return render_template('generos.html', generos = generos)


@app.route('/editar-genero/<int:id>', methods=['GET', 'POST'])
@login_required
def editar_genero(id):
    
    if current_user.tipo != 'Admin':
            return redirect(url_for('home'))

    genero = db.session.get(Genero, id)

    if not genero:
        return "Gênero não encontrado", 404

    if request.method == 'GET':
        return render_template(
            'editar_genero.html',
            genero=genero
        )

    nome = request.form['nomeForm'].strip()

    if not nome:
        return render_template(
            'editar_genero.html',
            genero=genero,
            erro='O nome do gênero é obrigatório'
        )

    genero.nome = nome

    db.session.commit()

    return redirect(url_for('generos'))

@app.route('/deletar-genero/<int:id>')
@login_required
def deletar_genero(id):
    
    if current_user.tipo != 'Admin':
            return redirect(url_for('home'))

    genero = db.session.get(Genero, id)

    if not genero:
        return "Gênero não encontrado", 404

    db.session.delete(genero)
    db.session.commit()

    return redirect(url_for('generos'))

@app.route('/registrar_genero', methods = ['GET', 'POST'])
@login_required
def registrar_genero():
    
    if current_user.tipo != 'Admin':
            return redirect(url_for('home'))
    
    if request.method == 'GET':
       return render_template('registrar_genero.html')
    elif request.method == 'POST':
        
        nome = request.form['nomeForm'].strip()

        if not nome:
            return render_template(
                'registrar_genero.html',
                erro='O nome do gênero é obrigatório'
            )
            
        novo_genero = Genero(nome=nome)

        db.session.add(novo_genero)
        db.session.commit()

        return redirect(url_for('generos'))


@app.route('/registrar_user', methods=['GET', 'POST'])
def registrar_user():
    
    if request.method == 'GET':
        return render_template('registrar_user.html')
    elif request.method == 'POST':
        
        nome = request.form['nomeForm'].strip()
        email = request.form['emailForm'].strip()
        senha = request.form['senhaForm'].strip()

        if not nome:
            return render_template('registrar_user.html', erro='O nome é obrigatório')

        if not email:
            return render_template('registrar_user.html', erro='O e-mail é obrigatório')

        if not senha:
            return render_template('registrar_user.html', erro='A senha é obrigatória')
        
        usuario_existente = Usuario.query.filter_by(email=email).first()

        if usuario_existente:
            return render_template(
                'registrar_user.html',
                erro='Esse e-mail já está cadastrado'
             )
            
        if len(senha) < 6:
            return render_template(
                'registrar_user.html',
                erro='A senha deve ter pelo menos 6 caracteres'
            )
        
        novo_usuario = Usuario(
            email=email,
            nome = nome,
            senha=hash(senha)
        )
        db.session.add(novo_usuario)
        db.session.commit()

        login_user(novo_usuario)
        return redirect(url_for('home'))


@app.route('/logout')
@login_required
def logout():
    logout_user()

    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    
    if request.method == 'GET':
        return render_template('login.html')
    elif request.method == 'POST':
        
        email = request.form['emailForm']
        senha = request.form['senhaForm']

        user = db.session.query(Usuario).filter_by(
            email = email,
            senha = hash(senha)
        ).first()

        if not user:
            return render_template(
        'login.html',
        login_incorreto='Email ou senha incorretos.'
    )
        
        login_user(user)
        
        return redirect(url_for('home'))
    
    
@app.route('/usuarios')
@login_required
def usuarios():
    
    if current_user.tipo != 'Admin':
        return redirect(url_for('home'))
    
    usuarios = Usuario.query.all()

    return render_template('usuarios.html', usuarios = usuarios)

@app.route('/remover_adm/<int:id>')
@login_required
def remover_adm(id):
    
    if current_user.tipo != 'Admin':
        return redirect(url_for('home'))
        
    usuario = db.session.query(Usuario).filter_by(id = id).first()

    if not usuario:
        return "Usuário não encontrado", 404


    usuario.tipo = 'comprador'
    db.session.commit()
    return redirect(url_for('usuarios'))
    
@app.route('/tornar_adm/<int:id>')
@login_required
def tornar_adm(id):
    
    if current_user.tipo != 'Admin':
        return redirect(url_for('home'))
    
    usuario = db.session.query(Usuario).filter_by(id = id).first()
    
    if not usuario:
        return "Usuário não encontrado", 404
    
    usuario.tipo = 'Admin'
    db.session.commit()
    return redirect(url_for('usuarios'))

@app.route('/deletar_user/<int:id>')
@login_required
def deletar_user(id):
    
    if current_user.tipo != 'Admin':
        return redirect(url_for('home'))
    
    usuario = db.session.query(Usuario).filter_by(id=id).first()

    if not usuario:
        return 'Usuario não encontrado', 404

    db.session.delete(usuario)
    db.session.commit()
    return redirect(url_for('usuarios'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()

    app.run(debug=True)
