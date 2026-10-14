from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from sqlalchemy import or_
from werkzeug.utils import secure_filename
import os
import uuid

from models import Livro, Genero, ItemVenda
from db import db

livros_bp = Blueprint('livros', __name__)

# Extensões de imagem permitidas
EXTENSOES_PERMITIDAS = {'png', 'jpg', 'jpeg', 'webp'}


def extensao_permitida(nome_arquivo):
    return (
        '.' in nome_arquivo
        and nome_arquivo.rsplit('.', 1)[1].lower()
        in EXTENSOES_PERMITIDAS
    )


# =========================
# REGISTRAR LIVRO
# =========================

@livros_bp.route('/registrar', methods=['GET', 'POST'])
@login_required
def registrar():

    if current_user.tipo not in ['admin', 'funcionario']:
        return redirect(url_for('home'))

    generos = Genero.query.filter_by(
        empresa_id=current_user.empresa_id
    ).all()

    if request.method == 'GET':
        return render_template(
            'livros/registrar.html',
            generos=generos
        )

    titulo = request.form['tituloForm'].strip()
    autor = request.form['autorForm'].strip()

    if not titulo:
        return render_template(
            'livros/registrar.html',
            generos=generos,
            erro='O título é obrigatório'
        )

    if not autor:
        return render_template(
            'livros/registrar.html',
            generos=generos,
            erro='O autor é obrigatório'
        )

    try:
        preco = float(request.form['precoForm'].strip())

    except ValueError:
        return render_template(
            'livros/registrar.html',
            generos=generos,
            erro='O preço é obrigatório e deve ser um número'
        )

    if preco < 0:
        return render_template(
            'livros/registrar.html',
            generos=generos,
            erro='O preço não pode ser negativo'
        )

    try:
        estoque = int(request.form['estoqueForm'].strip())

    except ValueError:
        return render_template(
            'livros/registrar.html',
            generos=generos,
            erro='O estoque é obrigatório e deve ser um número'
        )

    if estoque < 0:
        return render_template(
            'livros/registrar.html',
            generos=generos,
            erro='O estoque não pode ser negativo'
        )

    try:
        genero_id = int(request.form['genero_id'].strip())

    except ValueError:
        return render_template(
            'livros/registrar.html',
            generos=generos,
            erro='O gênero é obrigatório'
        )

    # Recebe a imagem enviada pelo formulário
    arquivo = request.files.get('campo_imagem')

    nome_imagem = 'padrao.png'

    if arquivo and arquivo.filename:
        # Verifica se a extensão é permitida
        if not extensao_permitida(arquivo.filename):
            flash(
                'Formato inválido! Envie PNG, JPG, JPEG ou WEBP.',
                'erro'
            )

            return render_template(
                'livros/registrar.html',
                generos=generos
            )

        # Higieniza o nome original do arquivo
        nome_seguro = secure_filename(arquivo.filename)

        if not nome_seguro:
            flash('Nome de arquivo inválido.', 'erro')

            return render_template(
                'livros/registrar.html',
                generos=generos
            )

        # Gera um nome único para evitar sobrescrever outra foto
        import uuid

        nome_imagem = f"{uuid.uuid4().hex}_{nome_seguro}"

        # Cria o caminho da pasta de uploads
        pasta_uploads = os.path.join(
            current_app.root_path,
            'static',
            'uploads'
        )

        os.makedirs(pasta_uploads, exist_ok=True)

        # Salva a imagem no servidor
        arquivo.save(
            os.path.join(pasta_uploads, nome_imagem)
        )

    # Cria o livro com o nome da imagem
    novo_livro = Livro(
        titulo=titulo,
        autor=autor,
        preco=preco,
        estoque=estoque,
        genero_id=genero_id,
        empresa_id=current_user.empresa_id,
        imagem=nome_imagem
    )

    db.session.add(novo_livro)
    db.session.commit()

    flash('Livro cadastrado com sucesso!', 'sucesso')

    return redirect(url_for('livros.listar_livros'))


# =========================
# LISTAR LIVROS
# =========================

@livros_bp.route('/livros')
@login_required
def listar_livros():

    if current_user.tipo not in ['admin', 'funcionario']:
        return redirect(url_for('home'))

    busca = request.args.get('busca', '').strip()

    if busca:

        livros = Livro.query.join(Genero).filter(
            Livro.empresa_id == current_user.empresa_id,
            Genero.empresa_id == current_user.empresa_id,
            or_(
                Livro.titulo.ilike(f'%{busca}%'),
                Livro.autor.ilike(f'%{busca}%'),
                Genero.nome.ilike(f'%{busca}%')
            )
        ).all()

    else:

        livros = Livro.query.filter_by(
            empresa_id=current_user.empresa_id
        ).all()

    return render_template(
        'livros/livros.html',
        livros=livros,
        busca=busca
    )


# =========================
# EDITAR LIVRO
# =========================

@livros_bp.route('/editar/<int:id>', methods=['GET', 'POST'])
@login_required
def editar(id):

    if current_user.tipo not in ['admin', 'funcionario']:
        return redirect(url_for('home'))

    livro = Livro.query.filter_by(
        id=id,
        empresa_id=current_user.empresa_id
    ).first()

    if not livro:
        return "Livro não encontrado", 404

    generos = Genero.query.filter_by(
        empresa_id=current_user.empresa_id
    ).all()

    if request.method == 'GET':
        return render_template(
            'livros/editar.html',
            livro=livro,
            generos=generos
        )

    titulo = request.form['tituloForm'].strip()
    autor = request.form['autorForm'].strip()

    if not titulo:
        return render_template(
            'livros/editar.html',
            livro=livro,
            generos=generos,
            erro='O título é obrigatório'
        )

    if not autor:
        return render_template(
            'livros/editar.html',
            livro=livro,
            generos=generos,
            erro='O autor é obrigatório'
        )

    try:
        preco = float(request.form['precoForm'].strip())

    except ValueError:
        return render_template(
            'livros/editar.html',
            livro=livro,
            generos=generos,
            erro='O preço é obrigatório e deve ser um número'
        )

    if preco < 0:
        return render_template(
            'livros/editar.html',
            livro=livro,
            generos=generos,
            erro='O preço não pode ser negativo'
        )

    try:
        estoque = int(request.form['estoqueForm'].strip())

    except ValueError:
        return render_template(
            'livros/editar.html',
            livro=livro,
            generos=generos,
            erro='O estoque é obrigatório e deve ser um número'
        )

    if estoque < 0:
        return render_template(
            'livros/editar.html',
            livro=livro,
            generos=generos,
            erro='O estoque não pode ser negativo'
        )

    try:
        genero_id = int(request.form['genero_id'].strip())

    except ValueError:
        return render_template(
            'livros/editar.html',
            livro=livro,
            generos=generos,
            erro='O gênero é obrigatório'
        )

    
    # Recebe a nova imagem, caso o usuário selecione uma
    arquivo = request.files.get('campo_imagem')

    nome_imagem_antiga = livro.imagem
    nome_imagem_nova = nome_imagem_antiga

    # Só troca a imagem se um arquivo foi selecionado
    if arquivo and arquivo.filename:

        # Verifica a extensão permitida
        if not extensao_permitida(arquivo.filename):
            return render_template(
                'livros/editar.html',
                livro=livro,
                generos=generos,
                erro='Formato inválido! Envie PNG, JPG, JPEG ou WEBP.'
            )

        # Higieniza o nome do arquivo
        nome_seguro = secure_filename(arquivo.filename)

        if not nome_seguro:
            return render_template(
                'livros/editar.html',
                livro=livro,
                generos=generos,
                erro='Nome de arquivo inválido.'
            )

        # Gera um nome único para a nova imagem
        import uuid

        nome_imagem_nova = f"{uuid.uuid4().hex}_{nome_seguro}"

        # Define a pasta de uploads
        pasta_uploads = os.path.join(
            current_app.root_path,
            'static',
            'uploads'
        )

        os.makedirs(pasta_uploads, exist_ok=True)

        # Salva a nova imagem
        caminho_novo = os.path.join(
            pasta_uploads,
            nome_imagem_nova
        )

        arquivo.save(caminho_novo)

    # Atualiza os dados do livro
    livro.titulo = titulo
    livro.autor = autor
    livro.preco = preco
    livro.estoque = estoque
    livro.genero_id = genero_id
    livro.imagem = nome_imagem_nova

    try:
        db.session.commit()

    except Exception:
        db.session.rollback()

        # Remove a imagem nova se a atualização falhar
        if nome_imagem_nova != nome_imagem_antiga:
            caminho_novo = os.path.join(
                current_app.root_path,
                'static',
                'uploads',
                nome_imagem_nova
            )

            if os.path.isfile(caminho_novo):
                os.remove(caminho_novo)

        raise

    # Remove a capa antiga somente após salvar a alteração
    if (
        nome_imagem_antiga
        and nome_imagem_antiga != 'padrao.png'
        and nome_imagem_antiga != nome_imagem_nova
    ):
        caminho_antigo = os.path.join(
            current_app.root_path,
            'static',
            'uploads',
            nome_imagem_antiga
        )

        if os.path.isfile(caminho_antigo):
            os.remove(caminho_antigo)

    flash('Livro atualizado com sucesso!', 'sucesso')

    return redirect(url_for('livros.listar_livros'))




# =========================
# ATIVAR / INATIVAR LIVRO
# =========================

@livros_bp.route('/toggle/<int:id>', methods=['POST'])
@login_required
def toggle_livro(id):

    if current_user.tipo not in ['admin', 'funcionario']:
        return redirect(url_for('home'))

    livro = Livro.query.filter_by(
        id=id,
        empresa_id=current_user.empresa_id
    ).first_or_404()

    # Alterna entre ativo e inativo
    livro.ativo = not livro.ativo

    db.session.commit()

    if livro.ativo:
        flash('Livro reativado com sucesso!', 'sucesso')
    else:
        flash('Livro inativado com sucesso!', 'sucesso')

    return redirect(url_for('livros.listar_livros'))


# =========================
# EXCLUIR LIVRO INATIVO
# =========================

@livros_bp.route('/deletar/<int:id>', methods=['POST'])
@login_required
def deletar(id):

    if current_user.tipo not in ['admin', 'funcionario']:
        return redirect(url_for('home'))

    livro = Livro.query.filter_by(
        id=id,
        empresa_id=current_user.empresa_id
    ).first_or_404()

    # Só permite excluir livros inativos
    if livro.ativo:
        flash(
            'Inative o livro antes de excluí-lo definitivamente.',
            'erro'
        )
        return redirect(url_for('livros.listar_livros'))

    # Preserva o histórico de vendas
    item_vendido = ItemVenda.query.filter_by(
        livro_id=livro.id
    ).first()

    if item_vendido:
        flash(
            'Não é possível excluir este livro porque ele possui vendas registradas.',
            'erro'
        )
        return redirect(url_for('livros.listar_livros'))

    # Guarda a imagem antes de excluir o registro
    nome_imagem = livro.imagem

    db.session.delete(livro)
    db.session.commit()

    # Remove a capa personalizada após excluir o livro
    if nome_imagem and nome_imagem != 'padrao.png':
        caminho_imagem = os.path.join(
            current_app.root_path,
            'static',
            'uploads',
            nome_imagem
        )

        if os.path.isfile(caminho_imagem):
            os.remove(caminho_imagem)

    flash('Livro excluído definitivamente!', 'sucesso')

    return redirect(url_for('livros.listar_livros'))
