from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import login_required, current_user
from sqlalchemy import or_

from models import Livro, Genero
from db import db


livros_bp = Blueprint('livros', __name__)


# =========================
# REGISTRAR LIVRO
# =========================

@livros_bp.route('/registrar', methods=['GET', 'POST'])
@login_required
def registrar():

    if current_user.tipo not in ['dono', 'admin_empresa', 'funcionario']:
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

    novo_livro = Livro(
        titulo=titulo,
        autor=autor,
        preco=preco,
        estoque=estoque,
        genero_id=genero_id,
        empresa_id=current_user.empresa_id
    )

    db.session.add(novo_livro)
    db.session.commit()

    return redirect(url_for('livros.listar_livros'))


# =========================
# LISTAR LIVROS
# =========================

@livros_bp.route('/livros')
@login_required
def listar_livros():

    if current_user.tipo not in ['dono', 'admin_empresa', 'funcionario']:
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

    if current_user.tipo not in ['dono', 'admin_empresa', 'funcionario']:
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

    livro.titulo = titulo
    livro.autor = autor
    livro.preco = preco
    livro.estoque = estoque
    livro.genero_id = genero_id

    db.session.commit()

    return redirect(url_for('livros.listar_livros'))


# =========================
# DELETAR LIVRO
# =========================

@livros_bp.route('/deletar/<int:id>')
@login_required
def deletar(id):

    if current_user.tipo not in ['dono', 'admin_empresa', 'funcionario']:
        return redirect(url_for('home'))

    livro = Livro.query.filter_by(
        id=id,
        empresa_id=current_user.empresa_id
    ).first()

    if not livro:
        return "Livro não encontrado", 404

    # TODO: verificar se o livro possui itens de venda antes de excluir

    db.session.delete(livro)
    db.session.commit()

    return redirect(url_for('livros.listar_livros'))