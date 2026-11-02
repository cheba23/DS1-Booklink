from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from sqlalchemy import func

from models import Genero, Livro
from db import db


generos_bp = Blueprint('generos', __name__)


# ==========================================
# LISTAR GÊNEROS
# ==========================================

@generos_bp.route('/generos')
@login_required
def listar_generos():

    if current_user.tipo not in ['admin', 'funcionario']:
        return redirect(url_for('home'))

    generos = Genero.query.filter_by(
        empresa_id=current_user.empresa_id
    ).all()

    return render_template(
        'generos/generos.html',
        generos=generos
    )


# ==========================================
# EDITAR GÊNERO
# ==========================================

@generos_bp.route('/editar-genero/<int:id>', methods=['GET', 'POST'])
@login_required
def editar_genero(id):

    if current_user.tipo not in ['admin', 'funcionario']:
        return redirect(url_for('home'))

    # Procura o gênero somente dentro da empresa atual
    genero = Genero.query.filter_by(
        id=id,
        empresa_id=current_user.empresa_id
    ).first()

    if not genero:
        return "Gênero não encontrado", 404

    if request.method == 'GET':
        return render_template(
            'generos/editar_genero.html',
            genero=genero
        )

    nome = request.form.get('nomeForm', '').strip()

    if not nome:
        return render_template(
            'generos/editar_genero.html',
            genero=genero,
            erro='O nome do gênero é obrigatório'
        )

    if len(nome) > 50:
        return render_template(
            'generos/editar_genero.html',
            genero=genero,
            erro='O nome do gênero deve ter no máximo 50 caracteres'
        )

    genero_existente = Genero.query.filter(
        Genero.empresa_id == current_user.empresa_id,
        func.lower(Genero.nome) == nome.lower(),
        Genero.id != id
    ).first()

    if genero_existente:
        return render_template(
            'generos/editar_genero.html',
            genero=genero,
            erro='Já existe outro gênero com este nome.'
        )

    genero.nome = nome

    db.session.commit()
    flash('Gênero atualizado com sucesso!', 'sucesso')

    return redirect(url_for('generos.listar_generos'))


# ==========================================
# DELETAR GÊNERO
# ==========================================

@generos_bp.route('/deletar-genero/<int:id>', methods=['GET', 'POST'])
@login_required
def deletar_genero(id):

    if current_user.tipo not in ['admin', 'funcionario']:
        return redirect(url_for('home'))

    # Busca somente um gênero da própria empresa
    genero = Genero.query.filter_by(
        id=id,
        empresa_id=current_user.empresa_id
    ).first()

    if not genero:
        return "Gênero não encontrado", 404

    # Verifica se algum livro usa esse gênero
    livros = Livro.query.filter_by(
        genero_id=genero.id,
        empresa_id=current_user.empresa_id
    ).first()

    if livros:
        flash('Não é possível excluir um gênero que possui livros cadastrados.', 'erro')
        return redirect(url_for('generos.listar_generos'))

    # Exclui o gênero
    db.session.delete(genero)
    db.session.commit()
    flash('Gênero excluído definitivamente!', 'sucesso')

    return redirect(url_for('generos.listar_generos'))


# ==========================================
# CADASTRAR GÊNERO
# ==========================================

@generos_bp.route('/registrar_genero', methods=['GET', 'POST'])
@login_required
def registrar_genero():

    if current_user.tipo not in ['admin', 'funcionario']:
        return redirect(url_for('home'))

    if request.method == 'GET':
        return render_template('generos/registrar_genero.html')

    nome = request.form.get('nomeForm', '').strip()

    if not nome:
        return render_template(
            'generos/registrar_genero.html',
            erro='O nome do gênero é obrigatório'
        )

    if len(nome) > 50:
        return render_template(
            'generos/registrar_genero.html',
            erro='O nome do gênero deve ter no máximo 50 caracteres'
        )

    genero_existente = Genero.query.filter(
        Genero.empresa_id == current_user.empresa_id,
        func.lower(Genero.nome) == nome.lower()
    ).first()

    if genero_existente:
        return render_template(
            'generos/registrar_genero.html',
            erro='Já existe um gênero cadastrado com este nome.'
        )

    novo_genero = Genero(
        nome=nome,
        empresa_id=current_user.empresa_id
    )

    db.session.add(novo_genero)
    db.session.commit()
    flash('Gênero cadastrado com sucesso!', 'sucesso')

    return redirect(url_for('generos.listar_generos'))